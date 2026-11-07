from datetime import UTC, datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIRequestFactory, force_authenticate

from . import api_views
from .models import Experience, Project
from .querysets import with_star_summary
from .serializers import ExperienceSerializer, ProjectSerializer


class _LegacyStarSummary:
    """Keep the pre-optimization representation for the payload comparison."""
    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated
                    and request.user in obj.starred_by.all())


class _LegacyProjectSerializer(_LegacyStarSummary, ProjectSerializer):
    pass


class _LegacyExperienceSerializer(_LegacyStarSummary, ExperienceSerializer):
    pass


class StarSummaryQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.readers = [users.objects.create_user(username=f'query-reader-{i}') for i in range(10)]
        cls.reader = cls.readers[0]
        cls.outsider = users.objects.create_user(username='query-outsider')
        cls.owner = users.objects.create_superuser(username='query-owner')
        cls.projects = []
        cls.experiences = []
        for index in range(20):
            values = {'title': f'Query probe {index:02}', 'description': 'Keep this text.'}
            project = Project.objects.create(
                **values, project_type='Web', role='Developer', technologies='Django',
                live_url='https://example.com/',
            )
            experience = Experience.objects.create(
                **values, category='volunteer', started_at=datetime(2026, 11, 1, tzinfo=UTC),
            )
            project.starred_by.add(*cls.readers)
            experience.starred_by.add(*cls.readers)
            cls.projects.append(project)
            cls.experiences.append(experience)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.specs = (
            (Project, ProjectSerializer, _LegacyProjectSerializer,
             api_views.project_list, api_views.project_detail, api_views.project_star,
             'project_id', self.projects[0]),
            (Experience, ExperienceSerializer, _LegacyExperienceSerializer,
             api_views.experience_list, api_views.experience_detail, api_views.experience_star,
             'experience_id', self.experiences[0]),
        )

    def request(self, method='get', user=None, data=None):
        request = getattr(self.factory, method)('/api/v1/', data=data or {}, format='json')
        if user:
            force_authenticate(request, user=user)
        return request

    def assert_no_account_reads(self, queries):
        user_table = get_user_model()._meta.db_table.lower()
        for query in queries:
            self.assertNotIn(user_table, query['sql'].lower())

    def test_list_one_and_twenty_use_one_query_and_never_load_star_accounts(self):
        for model, _, _, view, _, _, _, _ in self.specs:
            for user in (None, self.reader, self.outsider):
                for count, filters in ((1, {'title': 'Query probe 00'}), (20, {})):
                    with self.subTest(model=model.__name__, user=str(user), count=count):
                        request = self.request(user=user, data=filters)
                        with patch.object(get_user_model(), 'from_db', wraps=get_user_model().from_db) as hydrate:
                            with self.assertNumQueries(1), CaptureQueriesContext(connection) as queries:
                                response = view(request)
                                response.render()
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(len(response.data), count)
                        self.assertEqual(hydrate.call_count, 0)
                        self.assert_no_account_reads(queries)
                        for item in response.data:
                            self.assertEqual(item['star_count'], 10)
                            self.assertEqual(item['is_starred'], user == self.reader)

    def test_detail_for_guest_member_and_outsider_uses_one_query(self):
        for model, _, _, _, detail, _, key, obj in self.specs:
            for user in (None, self.reader, self.outsider):
                with self.subTest(model=model.__name__, user=str(user)):
                    request = self.request(user=user)
                    with self.assertNumQueries(1), CaptureQueriesContext(connection) as queries:
                        response = detail(request, **{key: obj.pk})
                        response.render()
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.data['star_count'], 10)
                    self.assertEqual(response.data['is_starred'], user == self.reader)
                    self.assert_no_account_reads(queries)

    def test_payload_matches_old_prefetch_with_fewer_queries_and_no_user_objects(self):
        for model, serializer, legacy_serializer, _, _, _, _, _ in self.specs:
            for user in (AnonymousUser(), self.reader, self.outsider):
                with self.subTest(model=model.__name__, user=str(user)):
                    request = self.factory.get('/api/v1/')
                    request.user = user
                    with patch.object(get_user_model(), 'from_db', wraps=get_user_model().from_db) as hydrate:
                        with self.assertNumQueries(2):
                            old_data = legacy_serializer(
                                model.objects.prefetch_related('starred_by').order_by('id'),
                                many=True, context={'request': request},
                            ).data
                        self.assertEqual(hydrate.call_count, 200)
                    with patch.object(get_user_model(), 'from_db', wraps=get_user_model().from_db) as hydrate:
                        with self.assertNumQueries(1):
                            new_data = serializer(
                                with_star_summary(model.objects.all(), user).order_by('id'),
                                many=True, context={'request': request},
                            ).data
                        self.assertEqual(hydrate.call_count, 0)
                    self.assertEqual(new_data, old_data)

    def test_materialized_summary_serializes_without_any_additional_queries(self):
        for model, serializer, _, _, _, _, _, _ in self.specs:
            request = self.factory.get('/api/v1/')
            request.user = self.reader
            objects = list(with_star_summary(model.objects.all(), self.reader))
            with self.subTest(model=model.__name__), self.assertNumQueries(0):
                data = serializer(objects, many=True, context={'request': request}).data
                self.assertEqual(len(data), 20)
                self.assertTrue(all(item['is_starred'] for item in data))

    def test_mine_keeps_total_count_and_never_multiplies_rows(self):
        for model, _, _, view, _, _, _, _ in self.specs:
            for user, count in ((self.reader, 20), (self.outsider, 0)):
                with self.subTest(model=model.__name__, user=str(user)):
                    with self.assertNumQueries(1):
                        response = view(self.request(user=user, data={'starred': 'mine'}))
                    self.assertEqual(response.status_code, 200)
                    ids = [item['id'] for item in response.data]
                    self.assertEqual(len(ids), count)
                    self.assertEqual(len(ids), len(set(ids)))
                    self.assertTrue(all(item['star_count'] == 10 for item in response.data))

    def test_empty_list_and_guest_mine_keep_the_public_contract(self):
        for model, _, _, view, _, _, _, _ in self.specs:
            with self.subTest(model=model.__name__):
                with self.assertNumQueries(1):
                    empty = view(self.request(data={'title': 'No matching role'}))
                self.assertEqual(empty.status_code, 200)
                self.assertEqual(empty.data, [])
                with self.assertNumQueries(0):
                    guest_mine = view(self.request(data={'starred': 'mine'}))
                self.assertEqual(guest_mine.status_code, 200)
                self.assertEqual(guest_mine.data, [])

    def test_plain_serializer_fallback_counts_and_checks_membership_without_loading_users(self):
        for model, serializer, _, _, _, _, _, obj in self.specs:
            for user in (AnonymousUser(), self.reader, self.outsider):
                with self.subTest(model=model.__name__, user=str(user)):
                    request = self.factory.get('/api/v1/')
                    request.user = user
                    plain = model.objects.get(pk=obj.pk)
                    with patch.object(get_user_model(), 'from_db', wraps=get_user_model().from_db) as hydrate:
                        with self.assertNumQueries(2 if user.is_authenticated else 1):
                            data = serializer(plain, context={'request': request}).data
                        self.assertEqual(hydrate.call_count, 0)
                    self.assertEqual(data['star_count'], 10)
                    self.assertEqual(data['is_starred'], user == self.reader)

    def test_toggle_reads_fresh_metadata_and_later_detail_remains_consistent(self):
        for model, _, _, _, detail, star, key, obj in self.specs:
            for expected, count in ((False, 9), (True, 10)):
                with self.subTest(model=model.__name__, starred=expected):
                    with patch.object(get_user_model(), 'from_db', wraps=get_user_model().from_db) as hydrate:
                        response = star(self.request('post', user=self.reader), **{key: obj.pk})
                        self.assertEqual(hydrate.call_count, 0)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.data['is_starred'], expected)
                    self.assertEqual(response.data['star_count'], count)
                    with self.assertNumQueries(1):
                        read = detail(self.request(user=self.reader), **{key: obj.pk})
                    self.assertEqual(read.data['is_starred'], expected)
                    self.assertEqual(read.data['star_count'], count)

    def test_annotated_patch_preserves_star_metadata_and_ignores_forged_fields(self):
        for model, _, _, _, detail, _, key, obj in self.specs:
            with self.subTest(model=model.__name__):
                response = detail(self.request('patch', self.owner, {
                    'title': 'Updated query probe', 'star_count': 99, 'is_starred': True,
                }), **{key: obj.pk})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['title'], 'Updated query probe')
                self.assertEqual(response.data['star_count'], 10)
                self.assertFalse(response.data['is_starred'])
                self.assertEqual(obj.starred_by.count(), 10)

    def test_create_plain_instance_returns_zero_stars_without_loading_accounts(self):
        for model, _, _, view, _, _, _, _ in self.specs:
            payload = {'title': 'New query probe', 'description': 'Created without stars.'}
            if model is Project:
                payload.update(project_type='Web', role='Developer', technologies='Django',
                               live_url='https://example.com/')
            with self.subTest(model=model.__name__):
                with patch.object(get_user_model(), 'from_db', wraps=get_user_model().from_db) as hydrate:
                    response = view(self.request('post', self.owner, payload))
                    self.assertEqual(hydrate.call_count, 0)
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.data['star_count'], 0)
                self.assertFalse(response.data['is_starred'])
