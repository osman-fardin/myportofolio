from datetime import UTC, datetime
from html.parser import HTMLParser

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from rest_framework.test import APITestCase

from .models import Experience


class ExperienceStarredFilterAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.reader = users.objects.create_user(username='personal-reader-a')
        cls.other = users.objects.create_user(username='personal-reader-b')
        cls.editor = users.objects.create_user(username='personal-editor')
        cls.editor.user_permissions.add(Permission.objects.get(
            content_type__app_label='main', codename='change_experience',
        ))
        cls.owner = users.objects.create_superuser(username='personal-owner')
        cls.shared = Experience.objects.create(
            title='Mentoring shared', description='Help students.', category='volunteer',
            started_at=datetime(2026, 11, 1, tzinfo=UTC),
        )
        cls.completed = Experience.objects.create(
            title='Mentoring completed', description='Prepare lessons.', category='volunteer',
            started_at=datetime(2026, 10, 1, tzinfo=UTC),
            ended_at=datetime(2026, 10, 31, tzinfo=UTC),
        )
        cls.research = Experience.objects.create(
            title='Research A', description='Build tools.', category='research',
            started_at=datetime(2026, 10, 20, tzinfo=UTC),
        )
        cls.other_only = Experience.objects.create(
            title='Research only B', description='Study results.', category='research',
            started_at=datetime(2026, 10, 22, tzinfo=UTC),
        )
        cls.unstarred = Experience.objects.create(
            title='Unstarred role', description='Another role.', category='volunteer',
            started_at=datetime(2026, 11, 2, tzinfo=UTC),
        )
        cls.shared.starred_by.add(cls.reader, cls.other)
        cls.completed.starred_by.add(cls.reader)
        cls.research.starred_by.add(cls.reader)
        cls.other_only.starred_by.add(cls.other)

    def setUp(self):
        self.url = reverse('api:experience-list')

    def ids(self, response):
        self.assertEqual(response.status_code, 200)
        return [item['id'] for item in response.data]

    def snapshot(self):
        return (
            list(Experience.objects.order_by('id').values()),
            list(Experience.starred_by.through.objects.order_by('id').values()),
        )

    def test_personal_results_are_isolated_with_total_counts_and_public_fields(self):
        fields = {
            'id', 'title', 'description', 'description_points', 'category',
            'category_label', 'thumbnail', 'started_at', 'ended_at',
            'is_ongoing', 'star_count', 'is_starred',
        }
        for user, expected in (
            (self.reader, [self.shared, self.research, self.completed]),
            (self.other, [self.shared, self.other_only]),
            (self.editor, []), (self.owner, []),
        ):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                response = self.client.get(self.url, {'starred': 'mine'})
                ids = self.ids(response)
                self.assertEqual(ids, [str(item.pk) for item in expected])
                self.assertEqual(len(ids), len(set(ids)))
                for item in response.data:
                    self.assertEqual(set(item), fields)
                    self.assertTrue(item['is_starred'])
                    self.assertEqual(item['star_count'], 2 if item['id'] == str(self.shared.pk) else 1)
                    self.assertNotIn(user.username, str(item))

    def test_guest_mine_is_empty_200_and_head_has_no_body(self):
        self.assertEqual(self.ids(self.client.get(self.url, {'starred': 'mine'})), [])
        response = self.client.head(self.url, {'starred': 'mine'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')

    def test_mine_combines_with_title_category_and_status(self):
        self.client.force_authenticate(user=self.reader)
        for filters, expected in (
            ({'title': 'MENTORING'}, [self.shared, self.completed]),
            ({'category': 'research'}, [self.research]),
            ({'status': 'ongoing'}, [self.shared, self.research]),
            ({'status': 'completed'}, [self.completed]),
            ({'title': ' mentoring ', 'category': 'volunteer', 'status': 'ongoing'}, [self.shared]),
            ({'title': 'Research only B'}, []),
            ({'category': 'invalid'}, []),
            ({'status': 'invalid'}, [self.shared, self.research, self.completed]),
        ):
            with self.subTest(filters=filters):
                response = self.client.get(self.url, {'starred': 'mine', **filters})
                self.assertEqual(self.ids(response), [str(item.pk) for item in expected])

    def test_mine_is_trimmed_and_unknown_values_leave_the_public_list_unchanged(self):
        self.client.force_authenticate(user=self.reader)
        expected = self.ids(self.client.get(self.url, {'starred': 'mine'}))
        self.assertEqual(self.ids(self.client.get(self.url, {'starred': ' mine '})), expected)
        all_ids = self.ids(self.client.get(self.url))
        self.assertEqual(len(all_ids), 5)
        for value in ('', 'all', '1', 'MINE'):
            with self.subTest(value=value):
                self.assertEqual(self.ids(self.client.get(self.url, {'starred': value})), all_ids)

    def test_query_parameters_cannot_select_another_account_or_mutate_data(self):
        before = self.snapshot()
        forged = {
            'starred': 'mine', 'user_id': self.other.pk,
            'username': self.other.username, 'starred_by': self.other.pk,
        }
        self.client.force_authenticate(user=self.reader)
        self.assertEqual(self.ids(self.client.get(self.url, forged)), [
            str(self.shared.pk), str(self.research.pk), str(self.completed.pk),
        ])
        self.client.force_authenticate(user=None)
        self.assertEqual(self.ids(self.client.get(self.url, forged)), [])
        self.assertEqual(self.snapshot(), before)

    def test_unstar_removes_only_current_users_result_and_keeps_the_other_star(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.post(reverse('api:experience-star', args=[self.shared.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['is_starred'])
        self.assertEqual(response.data['star_count'], 1)
        self.assertNotIn(str(self.shared.pk), self.ids(self.client.get(self.url, {'starred': 'mine'})))
        self.client.force_authenticate(user=self.other)
        results = self.client.get(self.url, {'starred': 'mine'})
        shared = next(item for item in results.data if item['id'] == str(self.shared.pk))
        self.assertTrue(shared['is_starred'])
        self.assertEqual(shared['star_count'], 1)
        self.assertEqual(list(self.shared.starred_by.all()), [self.other])

    def test_creating_while_mine_is_active_does_not_automatically_star_the_record(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.url + '?starred=mine', {
            'title': 'Owner created role', 'description': 'Created while filtering.',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data['is_starred'])
        self.assertEqual(response.data['star_count'], 0)
        self.assertFalse(Experience.objects.get(pk=response.data['id']).starred_by.exists())
        self.assertEqual(self.ids(self.client.get(self.url, {'starred': 'mine'})), [])

    def test_mine_query_does_not_grant_create_permission(self):
        before = self.snapshot()
        for user in (None, self.reader, self.editor):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)
                response = self.client.post(self.url + '?starred=mine', {
                    'title': 'Forbidden role', 'description': 'Must not be saved.',
                }, format='json')
                self.assertEqual(response.status_code, 403)
                self.assertEqual(self.snapshot(), before)


class _PersonalFilterParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.by_id = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get('id'):
            self.by_id[attributes['id']] = attributes


class ExperienceStarredFilterPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.reader = users.objects.create_user(username='personal-page-reader')
        cls.editor = users.objects.create_user(username='personal-page-editor')
        cls.editor.user_permissions.add(Permission.objects.get(
            content_type__app_label='main', codename='change_experience',
        ))
        cls.staff = users.objects.create_user(username='personal-page-staff', is_staff=True)
        cls.owner = users.objects.create_superuser(username='personal-page-owner')

    def page(self, filters):
        response = self.client.get(reverse('main:show_experience'), filters)
        self.assertEqual(response.status_code, 200)
        parser = _PersonalFilterParser()
        parser.feed(response.content.decode())
        return response, parser.by_id

    def test_logged_in_mine_link_renders_checked_control_and_active_clear(self):
        self.client.force_login(self.reader)
        response, attributes = self.page({'starred': ' mine '})
        control = attributes['experience-starred-filter']
        self.assertEqual(control['type'], 'checkbox')
        self.assertEqual(control['name'], 'starred')
        self.assertEqual(control['value'], 'mine')
        self.assertIn('checked', control)
        self.assertEqual(attributes['experience-list']['data-starred-filter'], 'mine')
        self.assertNotIn('hidden', attributes['experience-filter-clear'])
        self.assertTrue(response.context['has_active_filters'])

    def test_guest_mine_link_keeps_the_filter_without_a_personal_checkbox(self):
        response, attributes = self.page({'starred': 'mine'})
        self.assertNotIn('experience-starred-filter', attributes)
        self.assertEqual(attributes['experience-list']['data-starred-filter'], 'mine')
        self.assertNotIn('hidden', attributes['experience-filter-clear'])
        self.assertTrue(response.context['has_active_filters'])
        api_response = self.client.get(reverse('api:experience-list'), {'starred': 'mine'})
        self.assertEqual(api_response.json(), [])

    def test_unknown_or_empty_filter_is_not_checked_or_marked_active(self):
        self.client.force_login(self.reader)
        for value in ('', 'all', '1', 'MINE'):
            with self.subTest(value=value):
                response, attributes = self.page({'starred': value})
                self.assertNotIn('checked', attributes['experience-starred-filter'])
                self.assertEqual(attributes['experience-list']['data-starred-filter'], '')
                self.assertIn('hidden', attributes['experience-filter-clear'])
                self.assertFalse(response.context['has_active_filters'])

    def test_checkbox_visibility_keeps_the_existing_role_flags(self):
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
                _, attributes = self.page({})
                self.assertEqual('experience-starred-filter' in attributes, user is not None)
                self.assertEqual(tuple(attributes['experience-list'][f'data-can-{action}']
                                       for action in ('star', 'change', 'delete')), expected)

    def test_combined_filters_remain_escaped_and_selected_on_the_page(self):
        self.client.force_login(self.reader)
        title = '<img src=x onerror="alert(1)">'
        response, attributes = self.page({
            'title': title, 'category': 'research', 'status': 'completed', 'starred': 'mine',
        })
        self.assertContains(response, f'value="{escape(title)}"')
        self.assertNotContains(response, title)
        self.assertEqual(response.context['category_filter'], 'research')
        self.assertEqual(response.context['status_filter'], 'completed')
        self.assertIn('checked', attributes['experience-starred-filter'])
