from datetime import UTC, datetime
from html.parser import HTMLParser
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from rest_framework.test import APIClient

from .models import Experience


class _ExperienceListParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attributes = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'div' and attributes.get('id') == 'experience-list':
            self.attributes = attributes


class ExperienceReadPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.reader = user_model.objects.create_user(
            username='experience-page-reader', password='test-password',
        )
        cls.editor = user_model.objects.create_user(
            username='experience-page-editor', password='test-password',
        )
        cls.staff = user_model.objects.create_user(
            username='experience-page-staff', is_staff=True,
        )
        cls.owner = user_model.objects.create_superuser(username='experience-page-owner')
        cls.change_permission = Permission.objects.get(
            content_type__app_label='main', codename='change_experience',
        )
        group = Group.objects.create(name='Editor')
        group.permissions.add(cls.change_permission)
        cls.editor.groups.add(group)
        cls.experience = Experience.objects.create(
            title='A role from the database', description='Mentor students.',
            category='part-time', started_at=datetime(2026, 11, 1, 2, tzinfo=UTC),
        )

    def parse_list(self, response):
        self.assertEqual(response.status_code, 200)
        parser = _ExperienceListParser()
        parser.feed(response.content.decode())
        self.assertTrue(parser.attributes)
        return parser.attributes

    def test_page_targets_drf_and_does_not_call_the_legacy_json_view(self):
        with patch('main.views.get_experiences_json', side_effect=AssertionError('Legacy JSON called')):
            response = self.client.get(reverse('main:show_experience'))
        attributes = self.parse_list(response)
        self.assertEqual(attributes['data-experiences-url'], reverse('api:experience-list'))
        self.assertNotContains(response, 'data-experiences-url="/api/experiences/"')
        self.assertNotIn('experience_list', response.context)
        self.assertContains(response, 'Loading experiences...')
        self.assertNotContains(response, self.experience.title)

    def test_role_flags_and_modal_visibility_follow_server_permissions(self):
        for user, expected in (
            (None, ('false', 'false', 'false')),
            (self.reader, ('true', 'false', 'false')),
            (self.editor, ('true', 'true', 'false')),
            (self.staff, ('true', 'false', 'false')),
            (self.owner, ('true', 'true', 'true')),
        ):
            with self.subTest(user=str(user)):
                self.client.logout()
                if user:
                    self.client.force_login(user)
                response = self.client.get(reverse('main:show_experience'))
                attributes = self.parse_list(response)
                self.assertEqual(tuple(attributes[f'data-can-{action}'] for action in (
                    'star', 'change', 'delete',
                )), expected)
                for modal in ('experience-create-modal', 'experience-delete-modal'):
                    if user == self.owner:
                        self.assertContains(response, f'id="{modal}"')
                    else:
                        self.assertNotContains(response, f'id="{modal}"')

    def test_direct_permission_enables_edit_without_staff_or_editor_group(self):
        user = get_user_model().objects.create_user(username='direct-page-editor')
        user.user_permissions.add(self.change_permission)
        self.assertFalse(user.groups.exists())
        self.assertFalse(user.is_staff)
        self.client.force_login(user)
        attributes = self.parse_list(self.client.get(reverse('main:show_experience')))
        self.assertEqual(attributes['data-can-change'], 'true')
        self.assertEqual(attributes['data-can-delete'], 'false')

    def test_named_action_patterns_keep_the_existing_mutation_routes(self):
        attributes = self.parse_list(self.client.get(reverse('main:show_experience')))
        placeholder = '00000000-0000-0000-0000-000000000000'
        for action, route in (
            ('update', 'main:update_experience'),
            ('delete', 'main:delete_experience'),
            ('star', 'main:toggle_experience_star'),
        ):
            with self.subTest(action=action):
                pattern = attributes[f'data-{action}-url']
                self.assertEqual(pattern, reverse(route, args=[placeholder]))
                self.assertEqual(
                    pattern.replace(placeholder, str(self.experience.pk)),
                    reverse(route, args=[self.experience.pk]),
                )

    def test_ordinary_and_editor_pages_supply_a_valid_csrf_token_without_create(self):
        for user in (self.reader, self.editor):
            with self.subTest(user=user.username):
                client = APIClient(enforce_csrf_checks=True)
                self.assertTrue(client.login(username=user.username, password='test-password'))
                response = client.get(reverse('main:show_experience'))
                attributes = self.parse_list(response)
                self.assertIn('csrftoken', client.cookies)
                self.assertTrue(attributes['data-csrf-token'])
                self.assertNotContains(response, 'id="experience-create-form"')
                star_url = attributes['data-star-url'].replace(
                    '00000000-0000-0000-0000-000000000000', str(self.experience.pk),
                )
                starred = client.post(star_url, HTTP_X_CSRFTOKEN=attributes['data-csrf-token'])
                self.assertEqual(starred.status_code, 200)
                self.assertTrue(starred.json()['is_starred'])
                self.assertTrue(self.experience.starred_by.filter(pk=user.pk).exists())

    def test_filter_values_are_preserved_and_html_escaped(self):
        title = '<img src=x onerror="alert(1)">'
        response = self.client.get(reverse('main:show_experience'), {
            'title': title, 'category': 'research', 'status': 'completed',
        })
        self.assertEqual(response.context['title_query'], title)
        self.assertEqual(response.context['category_filter'], 'research')
        self.assertEqual(response.context['status_filter'], 'completed')
        self.assertTrue(response.context['has_active_filters'])
        self.assertContains(response, f'value="{escape(title)}"')
        self.assertNotContains(response, title)

    def test_empty_database_keeps_loading_filter_and_result_containers(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse('main:show_experience'))
        attributes = self.parse_list(response)
        self.assertEqual(attributes['data-experiences-url'], reverse('api:experience-list'))
        self.assertContains(response, 'id="experience-filter-form"')
        self.assertContains(response, 'id="experience-result-count"')
        self.assertContains(response, 'Loading experiences...')
        self.assertContains(response, 'id="experience-filter-clear"')
