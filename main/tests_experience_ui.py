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
                if user in (self.editor, self.owner):
                    self.assertContains(response, 'id="experience-edit-modal"')
                else:
                    self.assertNotContains(response, 'id="experience-edit-modal"')

    def test_direct_permission_enables_edit_without_staff_or_editor_group(self):
        user = get_user_model().objects.create_user(username='direct-page-editor')
        user.user_permissions.add(self.change_permission)
        self.assertFalse(user.groups.exists())
        self.assertFalse(user.is_staff)
        self.client.force_login(user)
        attributes = self.parse_list(self.client.get(reverse('main:show_experience')))
        self.assertEqual(attributes['data-can-change'], 'true')
        self.assertEqual(attributes['data-can-delete'], 'false')
        self.assertContains(
            self.client.get(reverse('main:show_experience')), 'id="experience-edit-modal"',
        )

    def test_named_action_patterns_use_drf_star_and_keep_html_edit_delete(self):
        attributes = self.parse_list(self.client.get(reverse('main:show_experience')))
        placeholder = '00000000-0000-0000-0000-000000000000'
        for action, route in (
            ('update', 'main:update_experience'),
            ('delete', 'main:delete_experience'),
            ('star', 'api:experience-star'),
            ('detail', 'api:experience-detail'),
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
                self.assertEqual(starred.json()['id'], str(self.experience.pk))
                self.assertTrue(starred.json()['is_starred'])
                self.assertTrue(self.experience.starred_by.filter(pk=user.pk).exists())

    def test_guest_page_star_url_is_denied_without_changing_the_relation(self):
        attributes = self.parse_list(self.client.get(reverse('main:show_experience')))
        self.assertEqual(attributes['data-can-star'], 'false')
        url = attributes['data-star-url'].replace(
            '00000000-0000-0000-0000-000000000000', str(self.experience.pk),
        )
        response = APIClient(enforce_csrf_checks=True).post(url)
        self.assertEqual(response.status_code, 403)
        self.assertIn('detail', response.json())
        self.assertFalse(self.experience.starred_by.exists())

    def test_rendered_star_url_rejects_missing_csrf_and_an_expired_session(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.reader.username, password='test-password'))
        attributes = self.parse_list(client.get(reverse('main:show_experience')))
        url = attributes['data-star-url'].replace(
            '00000000-0000-0000-0000-000000000000', str(self.experience.pk),
        )
        response = client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertIn('CSRF', response.json()['detail'])
        self.assertFalse(self.experience.starred_by.exists())

        client.logout()
        response = client.post(url, HTTP_X_CSRFTOKEN=attributes['data-csrf-token'])
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('CSRF', response.json()['detail'])
        self.assertFalse(self.experience.starred_by.exists())

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


class _ExperienceCreateFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attributes = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'form' and attributes.get('id') == 'experience-create-form':
            self.attributes = attributes


class ExperienceCreatePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser(
            username='experience-create-page-owner', password='test-password',
        )
        cls.payload = {
            'title': 'New mentoring role',
            'description': 'Support students.\nPrepare materials.',
            'category': 'volunteer',
            'thumbnail': None,
            'started_at': '2026-11-01T09:30',
            'ended_at': None,
        }

    def client_and_form(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.owner.username, password='test-password'))
        page = client.get(reverse('main:show_experience'))
        self.assertEqual(page.status_code, 200)
        parser = _ExperienceCreateFormParser()
        parser.feed(page.content.decode())
        self.assertTrue(parser.attributes)
        self.assertEqual(parser.attributes['data-api-url'], reverse('api:experience-list'))
        return client, parser.attributes, client.cookies['csrftoken'].value

    def test_modal_api_target_creates_json_data_with_optional_nulls(self):
        client, form, token = self.client_and_form()
        response = client.post(form['data-api-url'], {
            **self.payload, 'title': ' <b>New mentoring role</b> ',
        }, format='json', HTTP_X_CSRFTOKEN=token)

        self.assertEqual(response.status_code, 201)
        experience = Experience.objects.get(pk=response.data['id'])
        self.assertEqual(experience.title, self.payload['title'])
        self.assertEqual(experience.description, self.payload['description'])
        self.assertIsNone(experience.thumbnail)
        self.assertIsNone(experience.ended_at)
        self.assertTrue(response.data['is_ongoing'])
        self.assertEqual(experience.started_at, datetime(2026, 11, 1, 9, 30, tzinfo=UTC))
        self.assertEqual(response.data['star_count'], 0)
        self.assertEqual(Experience.objects.count(), 1)

    def test_modal_keeps_native_html_create_and_the_same_date_interpretation(self):
        client, form, token = self.client_and_form()
        self.assertEqual(form['action'], reverse('main:create_experience'))
        response = client.post(form['action'], {
            **self.payload, 'thumbnail': '', 'ended_at': '',
        }, HTTP_X_CSRFTOKEN=token)

        self.assertRedirects(
            response, reverse('main:show_experience'), fetch_redirect_response=False,
        )
        experience = Experience.objects.get()
        self.assertEqual(experience.title, self.payload['title'])
        self.assertEqual(experience.started_at, datetime(2026, 11, 1, 9, 30, tzinfo=UTC))
        self.assertIsNone(experience.ended_at)

    def test_invalid_modal_json_returns_field_errors_without_saving(self):
        client, form, token = self.client_and_form()
        for changes, field in (
            ({'title': '<img src=x onerror=alert(1)>'}, 'title'),
            ({'ended_at': '2026-10-31T09:30'}, 'ended_at'),
        ):
            with self.subTest(changes=changes):
                response = client.post(
                    form['data-api-url'], {**self.payload, **changes},
                    format='json', HTTP_X_CSRFTOKEN=token,
                )
                self.assertEqual(response.status_code, 400)
                self.assertIsInstance(response.data[field], list)
                self.assertEqual(Experience.objects.count(), 0)

    def test_modal_json_without_csrf_is_rejected_without_saving(self):
        client, form, _ = self.client_and_form()
        response = client.post(form['data-api-url'], self.payload, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('CSRF', str(response.data['detail']))
        self.assertEqual(Experience.objects.count(), 0)

    def test_expired_session_cannot_create_from_the_rendered_modal_url(self):
        client, form, token = self.client_and_form()
        client.logout()
        response = client.post(
            form['data-api-url'], self.payload, format='json', HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('CSRF', str(response.data['detail']))
        self.assertEqual(Experience.objects.count(), 0)


class _ExperienceEditFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attributes = {}
        self.ids = []
        self.fields = []
        self.in_form = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get('id'):
            self.ids.append(attributes['id'])
        if tag == 'form':
            self.in_form = attributes.get('id') == 'experience-edit-form'
            if self.in_form:
                self.attributes = attributes
        if self.in_form and tag in ('input', 'textarea', 'select'):
            self.fields.append(attributes)

    def handle_endtag(self, tag):
        if tag == 'form':
            self.in_form = False


class ExperienceEditPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.editor = user_model.objects.create_user(
            username='experience-edit-page-editor', password='test-password',
        )
        cls.owner = user_model.objects.create_superuser(
            username='experience-edit-page-owner', password='test-password',
        )
        cls.change_permission = Permission.objects.get(
            content_type__app_label='main', codename='change_experience',
        )
        group = Group.objects.create(name='Editor')
        group.permissions.add(cls.change_permission)
        cls.editor.groups.add(group)
        cls.experience = Experience.objects.create(
            title='Edit this role', description='First point.\n\nSecond point.',
            category='research', thumbnail='https://example.com/preview.jpg',
            started_at=datetime(2026, 10, 1, 9, 30, 42, 123456, tzinfo=UTC),
            ended_at=datetime(2026, 11, 1, 9, 30, 57, tzinfo=UTC),
        )
        cls.experience.starred_by.add(cls.editor)

    def page_and_target(self, user=None):
        user = user or self.editor
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=user.username, password='test-password'))
        page = client.get(reverse('main:show_experience'))
        self.assertEqual(page.status_code, 200)
        parser = _ExperienceListParser()
        parser.feed(page.content.decode())
        url = parser.attributes['data-detail-url'].replace(
            '00000000-0000-0000-0000-000000000000', str(self.experience.pk),
        )
        self.assertEqual(url, reverse('api:experience-detail', args=[self.experience.pk]))
        return client, page, url, parser.attributes['data-csrf-token']

    def test_owner_page_has_six_edit_fields_with_unique_ids_and_html_fallback(self):
        _, page, _, _ = self.page_and_target(self.owner)
        parser = _ExperienceEditFormParser()
        parser.feed(page.content.decode())
        self.assertTrue(parser.attributes)
        self.assertEqual(parser.attributes['method'], 'post')
        self.assertEqual(parser.attributes['action'], reverse(
            'main:update_experience', args=['00000000-0000-0000-0000-000000000000'],
        ))
        fields = {field['name']: field for field in parser.fields}
        self.assertEqual(set(fields), {
            'csrfmiddlewaretoken', 'title', 'description', 'category',
            'thumbnail', 'started_at', 'ended_at', 'initial-started_at',
        })
        self.assertEqual(fields['initial-started_at']['type'], 'hidden')
        self.assertEqual(fields['title']['id'], 'edit_title')
        self.assertEqual(fields['started_at']['type'], 'datetime-local')
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertContains(page, 'aria-labelledby="experience-edit-title"')

    def test_editor_partial_patch_keeps_exact_dates_description_and_stars(self):
        client, _, url, token = self.page_and_target()
        original_start, original_end = self.experience.started_at, self.experience.ended_at
        listed = client.get(reverse('api:experience-list')).json()[0]
        self.assertEqual(listed['description'], self.experience.description)
        response = client.patch(url, {'title': ' <b>Updated role</b> '},
                                format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], str(self.experience.pk))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Updated role')
        self.assertEqual(self.experience.description, 'First point.\n\nSecond point.')
        self.assertEqual(self.experience.started_at, original_start)
        self.assertEqual(self.experience.ended_at, original_end)
        self.assertEqual(list(self.experience.starred_by.all()), [self.editor])

    def test_editor_can_clear_optional_fields_with_null_from_modal_target(self):
        client, _, url, token = self.page_and_target()
        response = client.patch(url, {'thumbnail': None, 'ended_at': None},
                                format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertIsNone(self.experience.thumbnail)
        self.assertIsNone(self.experience.ended_at)
        self.assertTrue(response.json()['is_ongoing'])
        self.assertTrue(response.json()['is_starred'])

    def test_invalid_modal_patch_does_not_change_the_record(self):
        client, _, url, token = self.page_and_target()
        original = list(Experience.objects.values())
        for payload, field in (
            ({'title': '<img src=x onerror=alert(1)>'}, 'title'),
            ({'ended_at': '2026-09-30T09:30'}, 'ended_at'),
        ):
            with self.subTest(payload=payload):
                response = client.patch(url, payload, format='json', HTTP_X_CSRFTOKEN=token)
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json())
                self.assertEqual(list(Experience.objects.values()), original)
                self.assertEqual(list(self.experience.starred_by.all()), [self.editor])

    def test_permission_revoked_after_page_render_prevents_modal_patch(self):
        client, _, url, token = self.page_and_target()
        self.editor.groups.clear()
        original = list(Experience.objects.values())
        response = client.patch(url, {'title': 'Denied edit'},
                                format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(list(Experience.objects.values()), original)

    def test_missing_csrf_and_expired_session_prevent_modal_patch(self):
        client, _, url, token = self.page_and_target()
        original = list(Experience.objects.values())
        response = client.patch(url, {'title': 'Denied edit'}, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('CSRF', response.json()['detail'])
        self.assertEqual(list(Experience.objects.values()), original)
        client.logout()
        response = client.patch(url, {'title': 'Denied edit'},
                                format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('CSRF', response.json()['detail'])
        self.assertEqual(list(Experience.objects.values()), original)


class _ExperienceDeleteFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attributes = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'form' and attributes.get('id') == 'experience-delete-form':
            self.attributes = attributes


class ExperienceDeletePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.owner = user_model.objects.create_superuser(
            username='experience-delete-page-owner', password='test-password',
        )
        cls.reader = user_model.objects.create_user(
            username='experience-delete-page-reader', password='test-password',
        )
        cls.editor = user_model.objects.create_user(
            username='experience-delete-page-editor', password='test-password',
        )
        cls.editor.user_permissions.add(Permission.objects.get(
            content_type__app_label='main', codename='change_experience',
        ))
        cls.staff = user_model.objects.create_user(
            username='experience-delete-page-staff', password='test-password', is_staff=True,
        )
        cls.experience = Experience.objects.create(
            title='Delete only this role', description='A temporary role.',
        )
        cls.experience.starred_by.add(cls.owner, cls.reader)
        cls.other = Experience.objects.create(
            title='Keep this role', description='An unrelated role.',
        )
        cls.other.starred_by.add(cls.editor)

    def owner_page_and_target(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.owner.username, password='test-password'))
        page = client.get(reverse('main:show_experience'))
        self.assertEqual(page.status_code, 200)
        parser = _ExperienceDeleteFormParser()
        parser.feed(page.content.decode())
        self.assertTrue(parser.attributes)
        url = parser.attributes['data-api-url'].replace(
            '00000000-0000-0000-0000-000000000000', str(self.experience.pk),
        )
        self.assertEqual(url, reverse('api:experience-detail', args=[self.experience.pk]))
        return client, page, parser.attributes, url, client.cookies['csrftoken'].value

    def database_snapshot(self):
        return (
            list(Experience.objects.order_by('id').values()),
            list(Experience.starred_by.through.objects.order_by('id').values()),
        )

    def test_owner_confirmation_has_api_target_and_native_post_fallback(self):
        _, page, attributes, _, _ = self.owner_page_and_target()
        self.assertEqual(attributes['method'], 'post')
        self.assertEqual(attributes['aria-busy'], 'false')
        self.assertEqual(attributes['action'], reverse(
            'main:delete_experience', args=['00000000-0000-0000-0000-000000000000'],
        ))
        self.assertContains(page, 'aria-labelledby="experience-delete-title"')
        self.assertContains(page, 'autofocus')
        self.assertNotContains(page, self.experience.title)

    def test_delete_via_rendered_api_target_returns_empty_204_and_preserves_other_data(self):
        client, _, _, url, token = self.owner_page_and_target()
        other_before = Experience.objects.filter(pk=self.other.pk).values().get()
        response = client.delete(url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertFalse(Experience.starred_by.through.objects.filter(
            experience_id=self.experience.pk,
        ).exists())
        self.assertEqual(Experience.objects.filter(pk=self.other.pk).values().get(), other_before)
        self.assertEqual(list(self.other.starred_by.all()), [self.editor])
        self.assertEqual(Experience.objects.count(), 1)

    def test_guest_reader_editor_and_staff_cannot_delete_from_the_rendered_target(self):
        _, _, _, url, _ = self.owner_page_and_target()
        original = self.database_snapshot()
        for user in (None, self.reader, self.editor, self.staff):
            with self.subTest(user=str(user)):
                client = APIClient(enforce_csrf_checks=True)
                if user:
                    self.assertTrue(client.login(username=user.username, password='test-password'))
                page = client.get(reverse('main:show_experience'))
                self.assertNotContains(page, 'id="experience-delete-form"')
                token = client.cookies['csrftoken'].value
                response = client.delete(url, HTTP_X_CSRFTOKEN=token)
                self.assertEqual(response.status_code, 403)
                self.assertNotIn('CSRF', response.json()['detail'])
                self.assertEqual(self.database_snapshot(), original)

    def test_missing_or_wrong_csrf_and_expired_session_do_not_delete(self):
        client, _, _, url, token = self.owner_page_and_target()
        original = self.database_snapshot()
        for headers in ({}, {'HTTP_X_CSRFTOKEN': 'invalid'}):
            response = client.delete(url, **headers)
            self.assertEqual(response.status_code, 403)
            self.assertIn('CSRF', response.json()['detail'])
            self.assertEqual(self.database_snapshot(), original)
        client.logout()
        response = client.delete(url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('CSRF', response.json()['detail'])
        self.assertEqual(self.database_snapshot(), original)

    def test_owner_demoted_after_confirmation_render_cannot_delete(self):
        client, _, _, url, token = self.owner_page_and_target()
        self.owner.is_superuser = False
        self.owner.save(update_fields=['is_superuser'])
        original = self.database_snapshot()
        response = client.delete(url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.database_snapshot(), original)

    def test_native_post_delete_still_redirects_and_preserves_the_other_record(self):
        client, _, attributes, _, token = self.owner_page_and_target()
        url = attributes['action'].replace(
            '00000000-0000-0000-0000-000000000000', str(self.experience.pk),
        )
        response = client.post(url, HTTP_X_CSRFTOKEN=token)
        self.assertRedirects(response, reverse('main:show_experience'), fetch_redirect_response=False)
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertTrue(Experience.objects.filter(pk=self.other.pk).exists())
