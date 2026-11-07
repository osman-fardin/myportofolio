from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from .models import Experience
from .permissions import IsPortfolioOwnerOrEditorOrReadOnly
from .serializers import ExperienceSerializer


class ExperienceSerializerTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='experience-reader', email='private@example.com',
        )
        self.started_at = datetime(2026, 11, 1, 2, tzinfo=UTC)
        self.ended_at = datetime(2026, 11, 6, 2, tzinfo=UTC)
        self.payload = {
            'title': 'Teaching assistant',
            'description': 'Build tools\n\n Mentor students ',
            'category': 'part-time',
            'thumbnail': 'https://example.com/teaching.png',
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat(),
        }
        self.experience = Experience.objects.create(
            **{**self.payload, 'started_at': self.started_at, 'ended_at': self.ended_at},
        )
        self.experience.starred_by.add(self.user)

    def test_public_representation_is_explicit_and_hides_star_accounts(self):
        data = ExperienceSerializer(self.experience).data

        self.assertEqual(set(data), {
            'id', 'title', 'description', 'description_points', 'category',
            'category_label', 'thumbnail', 'started_at', 'ended_at',
            'is_ongoing', 'star_count', 'is_starred',
        })
        self.assertEqual(data['id'], str(self.experience.pk))
        self.assertEqual(data['description'], self.payload['description'])
        self.assertEqual(data['description_points'], ['Build tools', 'Mentor students'])
        self.assertEqual(data['category_label'], 'Part-Time')
        self.assertEqual(data['started_at'], '2026-11-01T02:00:00Z')
        self.assertEqual(data['ended_at'], '2026-11-06T02:00:00Z')
        self.assertFalse(data['is_ongoing'])
        self.assertEqual(data['star_count'], 1)
        self.assertFalse(data['is_starred'])
        self.assertNotIn(self.user.username, str(data))
        self.assertNotIn(self.user.email, str(data))
        self.assertNotIn(self.user.password, str(data))

    def test_star_status_follows_the_current_user(self):
        other = get_user_model().objects.create_user(username='other-experience-reader')
        factory = APIRequestFactory()

        for user, expected in (
            (self.user, True), (other, False), (AnonymousUser(), False),
        ):
            with self.subTest(user=str(user)):
                request = factory.get('/api/v1/experiences/')
                request.user = user
                data = ExperienceSerializer(
                    self.experience, context={'request': request},
                ).data
                self.assertEqual(data['is_starred'], expected)
                self.assertEqual(data['star_count'], 1)

        self.assertEqual(list(self.experience.starred_by.all()), [self.user])

    def test_read_only_update_cannot_forge_identity_properties_or_stars(self):
        before = list(Experience.objects.values())
        serializer = ExperienceSerializer(self.experience, data={
            'id': str(uuid4()),
            'description_points': ['Forged text'],
            'category_label': 'Forged category',
            'is_ongoing': True,
            'star_count': 99,
            'is_starred': False,
            'starred_by': [],
        }, partial=True)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data, {})
        serializer.save()

        self.assertEqual(list(Experience.objects.values()), before)
        self.assertEqual(list(self.experience.starred_by.all()), [self.user])

    def test_create_ignores_forged_computed_fields_and_account_ids(self):
        forged_id = uuid4()
        serializer = ExperienceSerializer(data={
            **self.payload,
            'ended_at': None,
            'id': str(forged_id),
            'description_points': ['Forged text'],
            'category_label': 'Forged category',
            'is_ongoing': False,
            'star_count': 99,
            'is_starred': True,
            'starred_by': [self.user.pk],
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        experience = serializer.save()
        self.assertNotEqual(experience.pk, forged_id)
        self.assertEqual(serializer.data['star_count'], 0)
        self.assertFalse(serializer.data['is_starred'])
        self.assertTrue(serializer.data['is_ongoing'])
        self.assertEqual(serializer.data['category_label'], 'Part-Time')
        self.assertEqual(experience.starred_by.count(), 0)
        self.assertEqual(Experience.objects.count(), 2)

    def test_create_cleans_required_text_before_saving(self):
        serializer = ExperienceSerializer(data={
            **self.payload,
            'title': ' <b>Teaching assistant</b> ',
            'description': ' <b>Build tools</b>\n\n <i>Mentor students</i> ',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        experience = serializer.save()
        experience.refresh_from_db()
        self.assertEqual(experience.title, 'Teaching assistant')
        self.assertEqual(experience.description, 'Build tools\n\n Mentor students')
        self.assertEqual(experience.description_points, ['Build tools', 'Mentor students'])

    def test_empty_or_tag_only_required_text_is_rejected(self):
        for field in ('title', 'description'):
            for value in ('', '   ', '<img src="x" onerror="alert(1)">'):
                with self.subTest(field=field, value=value):
                    serializer = ExperienceSerializer(data={**self.payload, field: value})
                    self.assertFalse(serializer.is_valid())
                    self.assertIn(field, serializer.errors)

        self.assertEqual(Experience.objects.count(), 1)

    def test_invalid_model_fields_and_dates_are_rejected(self):
        for field, value in (
            ('title', 'x' * 256),
            ('category', 'unknown'),
            ('thumbnail', 'javascript:alert(1)'),
            ('thumbnail', 'not-a-url'),
            ('started_at', 'not-a-date'),
            ('started_at', None),
            ('ended_at', 'not-a-date'),
            ('ended_at', ''),
        ):
            with self.subTest(field=field, value=value):
                serializer = ExperienceSerializer(data={**self.payload, field: value})
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

        self.assertEqual(Experience.objects.count(), 1)

    def test_create_uses_model_defaults_for_omitted_fields(self):
        default_start = datetime(2026, 11, 7, 2, tzinfo=UTC)
        field = Experience._meta.get_field('started_at')
        with patch.object(field, 'get_default', return_value=default_start) as get_default:
            serializer = ExperienceSerializer(data={
                'title': 'New experience', 'description': 'An ongoing role.',
            })
            self.assertTrue(serializer.is_valid(), serializer.errors)
            experience = serializer.save()
            get_default.assert_called_once_with()

        experience.refresh_from_db()
        self.assertEqual(experience.started_at, default_start)
        self.assertEqual(experience.category, 'full-time')
        self.assertIsNone(experience.thumbnail)
        self.assertIsNone(experience.ended_at)
        self.assertTrue(serializer.data['is_ongoing'])

    def test_create_compares_end_against_the_default_start(self):
        field = Experience._meta.get_field('started_at')
        with patch.object(field, 'get_default', return_value=self.ended_at):
            serializer = ExperienceSerializer(data={
                'title': 'Invalid finished role',
                'description': 'An end before the default start.',
                'ended_at': self.started_at.isoformat(),
            })
            self.assertFalse(serializer.is_valid())
            self.assertIn('ended_at', serializer.errors)

        self.assertEqual(Experience.objects.count(), 1)

    def test_end_may_equal_start_or_be_null_and_thumbnail_may_be_blank(self):
        for end in (self.started_at.isoformat(), None):
            with self.subTest(end=end):
                serializer = ExperienceSerializer(data={
                    **self.payload, 'ended_at': end, 'thumbnail': '',
                })
                self.assertTrue(serializer.is_valid(), serializer.errors)
                experience = serializer.save()
                self.assertEqual(experience.is_ongoing, end is None)
                self.assertEqual(experience.thumbnail, '')

    def test_full_update_changes_the_existing_record_and_keeps_stars(self):
        original_id = self.experience.pk
        serializer = ExperienceSerializer(self.experience, data={
            **self.payload,
            'title': '<b>Research assistant</b>',
            'description': 'A new responsibility.',
            'category': 'research',
            'thumbnail': None,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.pk, original_id)
        self.assertEqual(self.experience.title, 'Research assistant')
        self.assertEqual(self.experience.description, 'A new responsibility.')
        self.assertEqual(self.experience.category, 'research')
        self.assertIsNone(self.experience.thumbnail)
        self.assertEqual(Experience.objects.count(), 1)
        self.assertEqual(list(self.experience.starred_by.all()), [self.user])

    def test_full_update_requires_text_and_preserves_omitted_optional_fields(self):
        invalid = ExperienceSerializer(self.experience, data={'title': 'Incomplete'})
        self.assertFalse(invalid.is_valid())
        self.assertIn('description', invalid.errors)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, self.payload['title'])

        serializer = ExperienceSerializer(self.experience, data={
            'title': 'Replacement', 'description': 'Replacement description.',
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.started_at, self.started_at)
        self.assertEqual(self.experience.ended_at, self.ended_at)
        self.assertEqual(self.experience.category, self.payload['category'])
        self.assertEqual(self.experience.thumbnail, self.payload['thumbnail'])

    def test_partial_update_sanitizes_text_and_preserves_other_data(self):
        serializer = ExperienceSerializer(
            self.experience, data={'title': ' <b>Updated title</b> '}, partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.experience.refresh_from_db()

        self.assertEqual(self.experience.title, 'Updated title')
        self.assertEqual(self.experience.description, self.payload['description'])
        self.assertEqual(self.experience.started_at, self.started_at)
        self.assertEqual(self.experience.ended_at, self.ended_at)
        self.assertEqual(list(self.experience.starred_by.all()), [self.user])
        self.assertEqual(Experience.objects.count(), 1)

    def test_partial_start_after_stored_end_is_rejected_without_mutation(self):
        before = list(Experience.objects.values())
        serializer = ExperienceSerializer(self.experience, data={
            'started_at': '2026-11-08T02:00:00Z',
        }, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertIn('ended_at', serializer.errors)
        self.assertEqual(list(Experience.objects.values()), before)
        self.assertEqual(list(self.experience.starred_by.all()), [self.user])

    def test_partial_end_before_stored_start_is_rejected_without_mutation(self):
        before = list(Experience.objects.values())
        serializer = ExperienceSerializer(self.experience, data={
            'ended_at': '2026-10-31T02:00:00Z',
        }, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertIn('ended_at', serializer.errors)
        self.assertEqual(list(Experience.objects.values()), before)
        self.assertEqual(list(self.experience.starred_by.all()), [self.user])

    def test_partial_can_move_both_dates_to_a_new_valid_range(self):
        serializer = ExperienceSerializer(self.experience, data={
            'started_at': '2026-11-08T02:00:00Z',
            'ended_at': '2026-11-09T02:00:00Z',
        }, partial=True)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.started_at, datetime(2026, 11, 8, 2, tzinfo=UTC))
        self.assertEqual(self.experience.ended_at, datetime(2026, 11, 9, 2, tzinfo=UTC))

    def test_partial_can_clear_end_to_make_an_experience_ongoing(self):
        serializer = ExperienceSerializer(
            self.experience, data={'ended_at': None}, partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.experience.refresh_from_db()

        self.assertIsNone(self.experience.ended_at)
        self.assertTrue(serializer.data['is_ongoing'])
        self.assertEqual(self.experience.started_at, self.started_at)

    def test_invalid_partial_fields_do_not_change_stored_data(self):
        before = list(Experience.objects.values())
        for changes in (
            {'title': '   '},
            {'description': '<img src="x">'},
            {'category': 'unknown'},
            {'thumbnail': 'javascript:alert(1)'},
        ):
            with self.subTest(changes=changes):
                serializer = ExperienceSerializer(self.experience, data=changes, partial=True)
                self.assertFalse(serializer.is_valid())
                self.assertEqual(list(Experience.objects.values()), before)

    def test_date_comparison_uses_instants_across_timezone_offsets(self):
        serializer = ExperienceSerializer(data={
            **self.payload,
            'started_at': '2026-11-01T09:00:00+07:00',
            'ended_at': '2026-11-01T03:00:00Z',
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        experience = serializer.save()
        self.assertEqual(experience.started_at, self.started_at)

        invalid = ExperienceSerializer(data={
            **self.payload,
            'started_at': '2026-11-01T09:00:00+07:00',
            'ended_at': '2026-11-01T01:00:00Z',
        })
        self.assertFalse(invalid.is_valid())
        self.assertIn('ended_at', invalid.errors)


class ExperiencePermissionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.reader = user_model.objects.create_user(username='experience-api-reader')
        cls.editor = user_model.objects.create_user(username='experience-api-editor')
        cls.staff = user_model.objects.create_user(
            username='experience-api-staff', is_staff=True,
        )
        cls.owner = user_model.objects.create_superuser(username='experience-api-owner')
        cls.change_permission = Permission.objects.get(
            content_type__app_label='main', codename='change_experience',
        )
        cls.editor_group = Group.objects.create(name='Editor')
        cls.editor_group.permissions.add(cls.change_permission)
        cls.editor.groups.add(cls.editor_group)

    def is_allowed(self, user, method):
        request = APIRequestFactory().generic(method, '/api/v1/experiences/')
        request.user = user
        return IsPortfolioOwnerOrEditorOrReadOnly().has_permission(request, view=None)

    def test_every_role_can_read_without_write_permission(self):
        for user in (AnonymousUser(), self.reader, self.editor, self.staff, self.owner):
            for method in ('GET', 'HEAD', 'OPTIONS'):
                with self.subTest(user=str(user), method=method):
                    self.assertTrue(self.is_allowed(user, method))

    def test_guest_and_regular_user_cannot_write(self):
        for user in (AnonymousUser(), self.reader):
            for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                with self.subTest(user=str(user), method=method):
                    self.assertFalse(self.is_allowed(user, method))

    def test_editor_can_put_and_patch(self):
        self.assertTrue(self.editor.has_perm('main.change_experience'))
        self.assertFalse(self.editor.is_superuser)
        self.assertFalse(self.editor.is_staff)
        for method in ('PUT', 'PATCH'):
            with self.subTest(method=method):
                self.assertTrue(self.is_allowed(self.editor, method))

    def test_editor_cannot_create_delete_or_use_other_unsafe_methods(self):
        for method in ('POST', 'DELETE', 'TRACE'):
            with self.subTest(method=method):
                self.assertFalse(self.is_allowed(self.editor, method))

    def test_superuser_can_create_update_and_delete(self):
        for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            with self.subTest(method=method):
                self.assertTrue(self.is_allowed(self.owner, method))

    def test_group_name_without_permission_does_not_grant_editor_access(self):
        # Each test has its own transaction; this does not change local groups.
        self.editor_group.permissions.clear()
        user = get_user_model().objects.create_user(username='editor-name-only')
        user.groups.add(self.editor_group)
        self.assertTrue(user.groups.filter(name='Editor').exists())
        self.assertFalse(user.has_perm('main.change_experience'))

        for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            with self.subTest(method=method):
                self.assertFalse(self.is_allowed(user, method))

    def test_direct_model_permission_grants_only_update_with_or_without_staff(self):
        for is_staff in (False, True):
            user = get_user_model().objects.create_user(
                username=f'direct-experience-permission-{is_staff}', is_staff=is_staff,
            )
            user.user_permissions.add(self.change_permission)
            self.assertFalse(user.groups.exists())
            for method, expected in (
                ('PUT', True), ('PATCH', True), ('POST', False), ('DELETE', False),
            ):
                with self.subTest(is_staff=is_staff, method=method):
                    self.assertEqual(self.is_allowed(user, method), expected)

    def test_staff_and_project_permission_do_not_grant_experience_writes(self):
        project_editor = get_user_model().objects.create_user(username='project-only-editor')
        project_editor.user_permissions.add(Permission.objects.get(
            content_type__app_label='main', codename='change_project',
        ))
        self.assertTrue(project_editor.has_perm('main.change_project'))
        self.assertFalse(project_editor.has_perm('main.change_experience'))

        for user in (self.staff, project_editor):
            for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                with self.subTest(user=str(user), method=method):
                    self.assertFalse(self.is_allowed(user, method))


class ExperienceListAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.owner = user_model.objects.create_superuser(
            username='experience-list-owner', password='test-password',
        )
        cls.reader = user_model.objects.create_user(
            username='experience-list-reader', password='test-password',
        )
        cls.other_reader = user_model.objects.create_user(username='experience-list-other')
        cls.editor = user_model.objects.create_user(
            username='experience-list-editor', password='test-password',
        )
        cls.staff = user_model.objects.create_user(
            username='experience-list-staff', is_staff=True,
        )
        editor_group = Group.objects.create(name='Editor')
        editor_group.permissions.add(Permission.objects.get(
            content_type__app_label='main', codename='change_experience',
        ))
        cls.editor.groups.add(editor_group)
        cls.recent = Experience.objects.create(
            title='Teaching assistant', description='Build tools\nMentor students',
            category='part-time', started_at=datetime(2026, 11, 3, 2, tzinfo=UTC),
        )
        cls.completed = Experience.objects.create(
            title='Research mentor', description='An earlier research role.',
            category='research', started_at=datetime(2026, 11, 1, 2, tzinfo=UTC),
            ended_at=datetime(2026, 11, 2, 2, tzinfo=UTC),
        )
        cls.other_ongoing = Experience.objects.create(
            title='Teaching mentor', description='An ongoing research role.',
            category='research', started_at=datetime(2026, 11, 2, 2, tzinfo=UTC),
        )
        cls.recent.starred_by.add(cls.reader)
        cls.completed.starred_by.add(cls.other_reader)
        cls.payload = {
            'title': 'Volunteer mentor',
            'description': 'Support students.\nPrepare learning materials.',
            'category': 'volunteer',
            'thumbnail': 'https://example.com/volunteer.png',
            'started_at': '2026-11-01T02:00:00Z',
            'ended_at': '2026-11-02T02:00:00Z',
        }

    def setUp(self):
        self.list_url = reverse('api:experience-list')

    def database_snapshot(self):
        return (
            list(Experience.objects.order_by('id').values()),
            list(Experience.starred_by.through.objects.order_by('id').values()),
        )

    def session_client_and_token(self, user):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=user.username, password='test-password'))
        page = client.get(reverse('main:show_experience'))
        self.assertEqual(page.status_code, 200)
        self.assertIn('csrftoken', client.cookies)
        return client, client.cookies['csrftoken'].value

    def test_public_list_is_flat_private_and_personal_for_every_role(self):
        expected_fields = set(self.payload) | {
            'id', 'description_points', 'category_label', 'is_ongoing',
            'star_count', 'is_starred',
        }
        expected_ids = [
            str(self.recent.pk), str(self.other_ongoing.pk), str(self.completed.pk),
        ]
        for user in (
            None, self.reader, self.other_reader, self.editor, self.staff, self.owner,
        ):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)
                response = self.client.get(self.list_url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual([item['id'] for item in response.data], expected_ids)
                for item in response.data:
                    self.assertEqual(set(item), expected_fields)
                    self.assertEqual(
                        item['star_count'], int(item['id'] != str(self.other_ongoing.pk)),
                    )
                    expected_starred = (
                        (user == self.reader and item['id'] == str(self.recent.pk))
                        or (user == self.other_reader and item['id'] == str(self.completed.pk))
                    )
                    self.assertEqual(item['is_starred'], expected_starred)
                self.assertEqual(response.data[0]['description_points'], ['Build tools', 'Mentor students'])
                self.assertEqual(response.data[0]['category_label'], 'Part-Time')
                self.assertTrue(response.data[0]['is_ongoing'])
                self.assertIsNone(response.data[0]['ended_at'])
                self.assertFalse(response.data[-1]['is_ongoing'])
                self.assertNotIn(self.reader.username, str(response.data))
                self.assertNotIn(self.owner.password, str(response.data))

    def test_title_search_is_trimmed_case_insensitive_and_can_return_empty(self):
        for title, expected in (
            ('  TEACHING  ', [self.recent, self.other_ongoing]),
            ('no match', []),
            ('   ', [self.recent, self.other_ongoing, self.completed]),
        ):
            with self.subTest(title=title):
                response = self.client.get(self.list_url, {'title': title})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item['id'] for item in response.data], [str(item.pk) for item in expected],
                )

    def test_category_filter_preserves_the_legacy_no_results_behavior(self):
        for category, expected in (
            (' research ', [self.other_ongoing, self.completed]),
            ('part-time', [self.recent]),
            ('unknown', []),
        ):
            with self.subTest(category=category):
                response = self.client.get(self.list_url, {'category': category})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item['id'] for item in response.data], [str(item.pk) for item in expected],
                )

    def test_status_filter_preserves_ongoing_completed_and_unknown_behavior(self):
        for status_filter, expected in (
            (' ongoing ', [self.recent, self.other_ongoing]),
            ('completed', [self.completed]),
            ('unknown', [self.recent, self.other_ongoing, self.completed]),
        ):
            with self.subTest(status=status_filter):
                response = self.client.get(self.list_url, {'status': status_filter})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item['id'] for item in response.data], [str(item.pk) for item in expected],
                )

    def test_all_three_filters_can_be_combined(self):
        for status_filter, expected in (('ongoing', [self.other_ongoing]), ('completed', [])):
            with self.subTest(status=status_filter):
                response = self.client.get(self.list_url, {
                    'title': 'TEACHING', 'category': 'research', 'status': status_filter,
                })
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item['id'] for item in response.data], [str(item.pk) for item in expected],
                )

    def test_empty_database_returns_an_empty_array(self):
        Experience.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_ordering_uses_uuid_when_start_dates_are_equal(self):
        same_start = Experience.objects.create(
            title='Same start', description='Another role.', category='volunteer',
            started_at=self.recent.started_at,
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['id'] for item in response.data[:2]],
            sorted([str(same_start.pk), str(self.recent.pk)]),
        )

    def test_owner_can_create_cleaned_data_with_a_201_object_response(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, 'title': ' <b>Volunteer mentor</b> ',
            'description': '<i>Support students.</i>\nPrepare learning materials.',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        experience = Experience.objects.get(pk=response.data['id'])
        self.assertEqual(experience.title, self.payload['title'])
        self.assertEqual(experience.description, self.payload['description'])
        self.assertEqual(experience.category, 'volunteer')
        self.assertEqual(response.data['started_at'], self.payload['started_at'])
        self.assertEqual(response.data['ended_at'], self.payload['ended_at'])
        self.assertFalse(response.data['is_ongoing'])
        self.assertEqual(response.data['star_count'], 0)
        self.assertFalse(response.data['is_starred'])
        self.assertEqual(Experience.objects.count(), 4)

    def test_invalid_create_returns_field_errors_and_preserves_database(self):
        self.client.force_authenticate(user=self.owner)
        before = self.database_snapshot()
        for changes, field in (
            ({'title': '   '}, 'title'),
            ({'title': '<img src="x" onerror="alert(1)">'}, 'title'),
            ({'description': '<img src="x">'}, 'description'),
            ({'category': 'unknown'}, 'category'),
            ({'thumbnail': 'javascript:alert(1)'}, 'thumbnail'),
            ({'started_at': 'not-a-date'}, 'started_at'),
            ({'ended_at': '2026-10-31T02:00:00Z'}, 'ended_at'),
        ):
            with self.subTest(changes=changes):
                response = self.client.post(
                    self.list_url, {**self.payload, **changes}, format='json',
                )
                self.assertEqual(response.status_code, 400)
                self.assertIsInstance(response.data[field], list)
                self.assertEqual(self.database_snapshot(), before)

    def test_guest_reader_editor_and_staff_cannot_create_or_change_stars(self):
        before = self.database_snapshot()
        for user in (None, self.reader, self.editor, self.staff):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)
                response = self.client.post(self.list_url, self.payload, format='json')
                self.assertEqual(response.status_code, 403)
                self.assertIn('detail', response.data)
                self.assertEqual(self.database_snapshot(), before)

    def test_create_cannot_forge_id_computed_fields_or_star_accounts(self):
        self.client.force_authenticate(user=self.owner)
        forged_id = uuid4()
        response = self.client.post(self.list_url, {
            **self.payload, 'id': str(forged_id), 'description_points': ['Forged'],
            'category_label': 'Forged', 'is_ongoing': True, 'star_count': 99,
            'is_starred': True, 'starred_by': [self.reader.pk],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data['id'], str(forged_id))
        self.assertFalse(Experience.objects.filter(pk=forged_id).exists())
        experience = Experience.objects.get(pk=response.data['id'])
        self.assertEqual(experience.starred_by.count(), 0)
        self.assertEqual(response.data['star_count'], 0)
        self.assertFalse(response.data['is_starred'])
        self.assertFalse(response.data['is_ongoing'])
        self.assertEqual(response.data['category_label'], 'Volunteer')
        self.assertEqual(response.data['description_points'], self.payload['description'].splitlines())
        self.assertEqual(Experience.objects.count(), 4)

    def test_wrong_methods_follow_permission_then_method_checks_without_mutation(self):
        before = self.database_snapshot()
        for user, methods in (
            (self.owner, (('put', 405), ('patch', 405), ('delete', 405))),
            (self.editor, (('put', 405), ('patch', 405), ('delete', 403))),
            (self.reader, (('put', 403), ('patch', 403), ('delete', 403))),
            (None, (('put', 403), ('patch', 403), ('delete', 403))),
        ):
            for method, expected in methods:
                with self.subTest(user=str(user), method=method):
                    self.client.force_authenticate(user=user)
                    response = getattr(self.client, method)(self.list_url)
                    self.assertEqual(response.status_code, expected)
                    self.assertEqual(self.database_snapshot(), before)

    def test_malformed_json_returns_400_without_saving(self):
        self.client.force_authenticate(user=self.owner)
        before = self.database_snapshot()
        response = self.client.post(
            self.list_url, data='{"title":', content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertEqual(self.database_snapshot(), before)

    def test_public_head_and_options_do_not_change_data(self):
        before = self.database_snapshot()
        head = self.client.head(self.list_url)
        options = self.client.options(self.list_url)
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.content, b'')
        self.assertEqual(options.status_code, 200)
        self.assertEqual(set(options['Allow'].replace(' ', '').split(',')), {
            'GET', 'HEAD', 'POST', 'OPTIONS',
        })
        self.assertEqual(self.database_snapshot(), before)

    def test_browsable_api_and_json_format_are_available(self):
        page = self.client.get(self.list_url, HTTP_ACCEPT='text/html')
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.accepted_renderer.format, 'api')
        self.assertContains(page, reverse('rest_framework:login'))

        json_response = self.client.get(self.list_url, {'format': 'json'})
        self.assertEqual(json_response.status_code, 200)
        self.assertEqual(json_response.accepted_renderer.format, 'json')
        self.assertEqual(json_response.json()[0]['id'], str(self.recent.pk))

    def test_session_create_without_csrf_is_rejected_without_saving(self):
        client, _ = self.session_client_and_token(self.owner)
        before = self.database_snapshot()
        response = client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('CSRF', str(response.data['detail']))
        self.assertEqual(self.database_snapshot(), before)

    def test_session_create_with_wrong_csrf_is_rejected_without_saving(self):
        client, _ = self.session_client_and_token(self.owner)
        before = self.database_snapshot()
        response = client.post(
            self.list_url, self.payload, format='json', HTTP_X_CSRFTOKEN='invalid',
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn('CSRF', str(response.data['detail']))
        self.assertEqual(self.database_snapshot(), before)

    def test_session_create_with_csrf_succeeds(self):
        client, token = self.session_client_and_token(self.owner)
        response = client.post(
            self.list_url, self.payload, format='json', HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Experience.objects.filter(pk=response.data['id']).exists())
        self.assertEqual(Experience.objects.count(), 4)

    def test_reader_and_editor_sessions_with_valid_csrf_still_cannot_create(self):
        before = self.database_snapshot()
        for user in (self.reader, self.editor):
            with self.subTest(user=user.username):
                client, token = self.session_client_and_token(user)
                response = client.post(
                    self.list_url, self.payload, format='json', HTTP_X_CSRFTOKEN=token,
                )
                self.assertEqual(response.status_code, 403)
                self.assertIn('Only the portfolio owner', str(response.data['detail']))
                self.assertNotIn('CSRF', str(response.data['detail']))
                self.assertEqual(self.database_snapshot(), before)


class ExperienceDetailAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.owner = user_model.objects.create_superuser(
            username='experience-detail-owner', password='test-password',
        )
        cls.editor = user_model.objects.create_user(
            username='experience-detail-editor', password='test-password',
        )
        cls.reader = user_model.objects.create_user(
            username='experience-detail-reader', password='test-password',
        )
        cls.staff = user_model.objects.create_user(
            username='experience-detail-staff', is_staff=True,
        )
        cls.project_editor = user_model.objects.create_user(username='detail-project-editor')
        cls.project_editor.user_permissions.add(Permission.objects.get(
            content_type__app_label='main', codename='change_project',
        ))
        group = Group.objects.create(name='Editor')
        group.permissions.add(Permission.objects.get(
            content_type__app_label='main', codename='change_experience',
        ))
        cls.editor.groups.add(group)
        cls.payload = {
            'title': 'Teaching role',
            'description': 'Support students.\nBuild tools.',
            'category': 'part-time',
            'thumbnail': 'https://example.com/teaching.png',
            'started_at': '2026-11-01T02:00:00Z',
            'ended_at': '2026-11-06T02:00:00Z',
        }
        cls.experience = Experience.objects.create(**{
            **cls.payload,
            'started_at': datetime(2026, 11, 1, 2, tzinfo=UTC),
            'ended_at': datetime(2026, 11, 6, 2, tzinfo=UTC),
        })
        cls.other = Experience.objects.create(
            title='Keep this role', description='An unrelated ongoing role.',
            category='research', started_at=datetime(2026, 11, 2, 2, tzinfo=UTC),
        )
        cls.experience.starred_by.add(cls.reader, cls.editor)
        cls.other.starred_by.add(cls.reader)

    def setUp(self):
        self.detail_url = reverse('api:experience-detail', args=[self.experience.pk])

    def database_snapshot(self):
        return (
            list(Experience.objects.order_by('id').values()),
            list(Experience.starred_by.through.objects.order_by('id').values()),
        )

    def session_client_and_token(self, user):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=user.username, password='test-password'))
        page = client.get(reverse('main:show_experience'))
        self.assertEqual(page.status_code, 200)
        return client, client.cookies['csrftoken'].value

    def test_detail_is_public_private_and_personal_for_every_role(self):
        expected_fields = set(self.payload) | {
            'id', 'description_points', 'category_label', 'is_ongoing',
            'star_count', 'is_starred',
        }
        before = self.database_snapshot()
        for user in (None, self.reader, self.editor, self.staff, self.project_editor, self.owner):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)
                response = self.client.get(self.detail_url)
                self.assertEqual(response.status_code, 200)
                self.assertIsInstance(response.data, dict)
                self.assertEqual(set(response.data), expected_fields)
                self.assertEqual(response.data['id'], str(self.experience.pk))
                self.assertEqual(response.data['description'], self.payload['description'])
                self.assertEqual(response.data['description_points'], ['Support students.', 'Build tools.'])
                self.assertEqual(response.data['category_label'], 'Part-Time')
                self.assertEqual(response.data['star_count'], 2)
                self.assertEqual(response.data['is_starred'], user in (self.reader, self.editor))
                self.assertNotIn(self.reader.username, str(response.data))
                self.assertNotIn(self.owner.password, str(response.data))
        self.assertEqual(self.database_snapshot(), before)

    def test_public_head_options_and_browsable_api_are_read_only(self):
        before = self.database_snapshot()
        head = self.client.head(self.detail_url)
        options = self.client.options(self.detail_url)
        page = self.client.get(self.detail_url, HTTP_ACCEPT='text/html')
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.content, b'')
        self.assertEqual(options.status_code, 200)
        self.assertEqual(set(options['Allow'].replace(' ', '').split(',')), {
            'GET', 'HEAD', 'PUT', 'PATCH', 'DELETE', 'OPTIONS',
        })
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.accepted_renderer.format, 'api')
        self.assertEqual(self.database_snapshot(), before)

    def test_missing_uuid_returns_404_for_requests_allowed_by_permission(self):
        missing = reverse('api:experience-detail', args=[uuid4()])
        before = self.database_snapshot()
        for user, methods in (
            (None, ('get',)),
            (self.editor, ('get', 'put', 'patch')),
            (self.owner, ('get', 'put', 'patch', 'delete')),
        ):
            self.client.force_authenticate(user=user)
            for method in methods:
                with self.subTest(user=str(user), method=method):
                    response = getattr(self.client, method)(
                        missing, self.payload if method in ('put', 'patch') else None,
                        format='json',
                    )
                    self.assertEqual(response.status_code, 404)
                    self.assertIn('detail', response.data)
                    self.assertEqual(self.database_snapshot(), before)
        self.assertEqual(self.client.get('/api/v1/experiences/not-a-uuid/').status_code, 404)

    def test_editor_and_owner_patch_only_the_submitted_field(self):
        before = self.database_snapshot()
        original = Experience.objects.values().get(pk=self.experience.pk)
        for index, user in enumerate((self.editor, self.owner)):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                title = f'Updated role {index}'
                response = self.client.patch(
                    self.detail_url, {'title': f' <b>{title}</b> '}, format='json',
                )
                self.assertEqual(response.status_code, 200)
                current = Experience.objects.values().get(pk=self.experience.pk)
                self.assertEqual(current, {**original, 'title': title})
                self.assertEqual(self.database_snapshot()[1], before[1])
                self.assertEqual(response.data['star_count'], 2)
                self.assertEqual(Experience.objects.count(), 2)
                self.other.refresh_from_db()
                self.assertEqual(self.other.title, 'Keep this role')

    def test_editor_and_owner_put_update_the_existing_record(self):
        stars_before = self.database_snapshot()[1]
        for index, user in enumerate((self.editor, self.owner)):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                response = self.client.put(self.detail_url, {
                    **self.payload, 'title': f'Replacement {index}',
                    'description': '<p>A replacement responsibility.</p>',
                    'category': 'research', 'thumbnail': None,
                    'started_at': '2026-11-08T02:00:00Z',
                    'ended_at': '2026-11-09T02:00:00Z',
                }, format='json')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['id'], str(self.experience.pk))
                self.experience.refresh_from_db()
                self.assertEqual(self.experience.title, f'Replacement {index}')
                self.assertEqual(self.experience.description, 'A replacement responsibility.')
                self.assertEqual(self.experience.category, 'research')
                self.assertIsNone(self.experience.thumbnail)
                self.assertEqual(self.experience.started_at, datetime(2026, 11, 8, 2, tzinfo=UTC))
                self.assertEqual(self.experience.ended_at, datetime(2026, 11, 9, 2, tzinfo=UTC))
                self.assertEqual(self.database_snapshot()[1], stars_before)
                self.assertEqual(Experience.objects.count(), 2)

    def test_invalid_put_and_patch_preserve_records_and_star_relations(self):
        before = self.database_snapshot()
        for user in (self.editor, self.owner):
            self.client.force_authenticate(user=user)
            for method, payload, field in (
                ('put', {'title': 'Incomplete'}, 'description'),
                ('put', {**self.payload, 'ended_at': '2026-10-31T02:00:00Z'}, 'ended_at'),
                ('patch', {'title': '<img src="x" onerror="alert(1)">'}, 'title'),
                ('patch', {'description': '<b></b>'}, 'description'),
                ('patch', {'category': 'unknown'}, 'category'),
                ('patch', {'thumbnail': 'javascript:alert(1)'}, 'thumbnail'),
                ('patch', {'started_at': None}, 'started_at'),
                ('patch', {'started_at': '2026-11-08T02:00:00Z'}, 'ended_at'),
                ('patch', {'ended_at': '2026-10-31T02:00:00Z'}, 'ended_at'),
                ('patch', {'ended_at': ''}, 'ended_at'),
            ):
                with self.subTest(user=user.username, method=method, payload=payload):
                    response = getattr(self.client, method)(self.detail_url, payload, format='json')
                    self.assertEqual(response.status_code, 400)
                    self.assertIsInstance(response.data[field], list)
                    self.assertEqual(self.database_snapshot(), before)

    def test_patch_can_move_both_dates_and_clear_end_for_ongoing(self):
        for user in (self.editor, self.owner):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                moved = self.client.patch(self.detail_url, {
                    'started_at': '2026-11-08T02:00:00Z',
                    'ended_at': '2026-11-09T02:00:00Z',
                }, format='json')
                self.assertEqual(moved.status_code, 200)
                self.assertEqual(moved.data['started_at'], '2026-11-08T02:00:00Z')
                self.assertFalse(moved.data['is_ongoing'])
                ongoing = self.client.patch(self.detail_url, {'ended_at': None}, format='json')
                self.assertEqual(ongoing.status_code, 200)
                self.assertTrue(ongoing.data['is_ongoing'])
                self.experience.refresh_from_db()
                self.assertIsNone(self.experience.ended_at)
                self.assertEqual(self.experience.started_at, datetime(2026, 11, 8, 2, tzinfo=UTC))
                self.assertEqual(self.experience.starred_by.count(), 2)

    def test_guest_reader_staff_and_project_editor_cannot_update_or_delete(self):
        before = self.database_snapshot()
        for user in (None, self.reader, self.staff, self.project_editor):
            self.client.force_authenticate(user=user)
            for method in ('put', 'patch', 'delete'):
                with self.subTest(user=str(user), method=method):
                    response = getattr(self.client, method)(
                        self.detail_url, {**self.payload, 'title': 'Forbidden'}, format='json',
                    )
                    self.assertEqual(response.status_code, 403)
                    self.assertIn('detail', response.data)
                    self.assertEqual(self.database_snapshot(), before)

    def test_editor_cannot_delete_even_with_the_change_permission(self):
        self.assertTrue(self.editor.has_perm('main.change_experience'))
        self.client.force_authenticate(user=self.editor)
        before = self.database_snapshot()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.database_snapshot(), before)

    def test_owner_delete_returns_empty_204_and_only_removes_its_target(self):
        self.client.force_authenticate(user=self.owner)
        other_before = Experience.objects.values().get(pk=self.other.pk)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertFalse(Experience.starred_by.through.objects.filter(
            experience_id=self.experience.pk,
        ).exists())
        self.assertEqual(Experience.objects.values().get(pk=self.other.pk), other_before)
        self.assertEqual(list(self.other.starred_by.all()), [self.reader])
        self.assertEqual(Experience.objects.count(), 1)
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_updates_ignore_forged_uuid_properties_and_star_accounts(self):
        stars_before = self.database_snapshot()[1]
        forged_id = uuid4()
        for user in (self.editor, self.owner):
            self.client.force_authenticate(user=user)
            for method in ('put', 'patch'):
                with self.subTest(user=user.username, method=method):
                    response = getattr(self.client, method)(self.detail_url, {
                        **self.payload, 'title': 'Allowed update', 'id': str(forged_id),
                        'description_points': ['Forged'], 'category_label': 'Forged',
                        'is_ongoing': True, 'star_count': 99, 'is_starred': False,
                        'starred_by': [],
                    }, format='json')
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.data['id'], str(self.experience.pk))
                    self.assertEqual(response.data['category_label'], 'Part-Time')
                    self.assertFalse(response.data['is_ongoing'])
                    self.assertEqual(response.data['star_count'], 2)
                    self.assertEqual(response.data['is_starred'], user == self.editor)
                    self.assertEqual(response.data['description_points'], self.payload['description'].splitlines())
                    self.assertEqual(self.database_snapshot()[1], stars_before)
                    self.assertFalse(Experience.objects.filter(pk=forged_id).exists())
                    self.assertEqual(Experience.objects.count(), 2)

    def test_post_to_detail_follows_permission_and_method_checks(self):
        before = self.database_snapshot()
        for user, expected in ((self.owner, 405), (self.editor, 403), (self.reader, 403), (None, 403)):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)
                response = self.client.post(self.detail_url, self.payload, format='json')
                self.assertEqual(response.status_code, expected)
                self.assertEqual(self.database_snapshot(), before)

    def test_malformed_json_update_does_not_change_data(self):
        before = self.database_snapshot()
        for user in (self.editor, self.owner):
            self.client.force_authenticate(user=user)
            for method in ('put', 'patch'):
                with self.subTest(user=user.username, method=method):
                    response = getattr(self.client, method)(
                        self.detail_url, data='{"title":', content_type='application/json',
                    )
                    self.assertEqual(response.status_code, 400)
                    self.assertIn('detail', response.data)
                    self.assertEqual(self.database_snapshot(), before)

    def test_forbidden_writes_are_denied_before_missing_object_lookup(self):
        missing = reverse('api:experience-detail', args=[uuid4()])
        before = self.database_snapshot()
        for user, methods in (
            (None, ('put', 'patch', 'delete')),
            (self.reader, ('put', 'patch', 'delete')),
            (self.editor, ('delete',)),
        ):
            self.client.force_authenticate(user=user)
            for method in methods:
                with self.subTest(user=str(user), method=method):
                    response = getattr(self.client, method)(missing, self.payload, format='json')
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(self.database_snapshot(), before)

    def test_session_mutations_without_csrf_are_rejected_without_changes(self):
        before = self.database_snapshot()
        for user in (self.editor, self.owner):
            client, _ = self.session_client_and_token(user)
            for method in ('put', 'patch', 'delete'):
                with self.subTest(user=user.username, method=method):
                    response = getattr(client, method)(self.detail_url, self.payload, format='json')
                    self.assertEqual(response.status_code, 403)
                    self.assertIn('CSRF', str(response.data['detail']))
                    self.assertEqual(self.database_snapshot(), before)

    def test_session_mutations_with_wrong_csrf_are_rejected_without_changes(self):
        before = self.database_snapshot()
        for user in (self.editor, self.owner):
            client, _ = self.session_client_and_token(user)
            for method in ('put', 'patch', 'delete'):
                with self.subTest(user=user.username, method=method):
                    response = getattr(client, method)(
                        self.detail_url, self.payload, format='json', HTTP_X_CSRFTOKEN='invalid',
                    )
                    self.assertEqual(response.status_code, 403)
                    self.assertIn('CSRF', str(response.data['detail']))
                    self.assertEqual(self.database_snapshot(), before)

    def test_owner_session_can_put_patch_and_delete_with_valid_csrf(self):
        client, token = self.session_client_and_token(self.owner)
        put = client.put(self.detail_url, {
            **self.payload, 'title': 'Session PUT',
        }, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(put.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Session PUT')

        patched = client.patch(self.detail_url, {
            'description': '<b>Session PATCH</b>',
        }, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(patched.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.description, 'Session PATCH')

        deleted = client.delete(self.detail_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(deleted.content, b'')
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertTrue(Experience.objects.filter(pk=self.other.pk).exists())
        self.assertEqual(list(self.other.starred_by.all()), [self.reader])

    def test_editor_session_can_update_but_cannot_delete_with_valid_csrf(self):
        client, token = self.session_client_and_token(self.editor)
        put = client.put(self.detail_url, {
            **self.payload, 'title': 'Editor PUT',
        }, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(put.status_code, 200)
        patched = client.patch(self.detail_url, {
            'title': '<b>Editor PATCH</b>',
        }, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(patched.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Editor PATCH')

        before = self.database_snapshot()
        deleted = client.delete(self.detail_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(deleted.status_code, 403)
        self.assertNotIn('CSRF', str(deleted.data['detail']))
        self.assertEqual(self.database_snapshot(), before)

    def test_reader_session_with_valid_csrf_cannot_update_or_delete(self):
        client, token = self.session_client_and_token(self.reader)
        before = self.database_snapshot()
        for method in ('put', 'patch', 'delete'):
            with self.subTest(method=method):
                response = getattr(client, method)(
                    self.detail_url, self.payload, format='json', HTTP_X_CSRFTOKEN=token,
                )
                self.assertEqual(response.status_code, 403)
                self.assertNotIn('CSRF', str(response.data['detail']))
                self.assertEqual(self.database_snapshot(), before)

    def test_put_with_required_text_preserves_omitted_optional_fields(self):
        original = Experience.objects.values().get(pk=self.experience.pk)
        for user in (self.editor, self.owner):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                response = self.client.put(self.detail_url, {
                    'title': 'Minimal replacement', 'description': 'Updated description.',
                }, format='json')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(Experience.objects.values().get(pk=self.experience.pk), {
                    **original, 'title': 'Minimal replacement', 'description': 'Updated description.',
                })


class ExperienceStarAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.reader = user_model.objects.create_user(
            username='experience-star-reader', password='test-password',
        )
        cls.other_reader = user_model.objects.create_user(username='experience-star-other')
        cls.editor = user_model.objects.create_user(
            username='experience-star-editor', password='test-password',
        )
        cls.staff = user_model.objects.create_user(
            username='experience-star-staff', is_staff=True,
        )
        cls.owner = user_model.objects.create_superuser(
            username='experience-star-owner', password='test-password',
        )
        group = Group.objects.create(name='Editor')
        group.permissions.add(Permission.objects.get(
            content_type__app_label='main', codename='change_experience',
        ))
        cls.editor.groups.add(group)
        cls.experience = Experience.objects.create(
            title='Star this role', description='Build tools.\nMentor students.',
            category='part-time', started_at=datetime(2026, 11, 1, 2, tzinfo=UTC),
        )
        cls.other = Experience.objects.create(
            title='Keep this role', description='Another ongoing role.',
            category='research', started_at=datetime(2026, 11, 2, 2, tzinfo=UTC),
        )
        cls.other.starred_by.add(cls.other_reader)

    def setUp(self):
        self.star_url = reverse('api:experience-star', args=[self.experience.pk])
        self.detail_url = reverse('api:experience-detail', args=[self.experience.pk])

    def database_snapshot(self):
        return (
            list(Experience.objects.order_by('id').values()),
            list(Experience.starred_by.through.objects.order_by('id').values()),
        )

    def session_client_and_token(self, user):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=user.username, password='test-password'))
        page = client.get(reverse('main:show_experience'))
        self.assertEqual(page.status_code, 200)
        return client, client.cookies['csrftoken'].value

    def test_guest_is_denied_before_method_checks_without_changing_data(self):
        before = self.database_snapshot()
        for method in ('get', 'post'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.star_url)
                self.assertEqual(response.status_code, 403)
                self.assertIn('detail', response.data)
                self.assertEqual(self.database_snapshot(), before)

    def test_every_authenticated_role_can_toggle_only_its_own_star(self):
        fields = {
            'id', 'title', 'description', 'description_points', 'category',
            'category_label', 'thumbnail', 'started_at', 'ended_at',
            'is_ongoing', 'star_count', 'is_starred',
        }
        records_before = self.database_snapshot()[0]
        for user in (self.reader, self.editor, self.staff, self.owner):
            self.client.force_authenticate(user=user)
            for expected in (True, False):
                with self.subTest(user=user.username, starred=expected):
                    response = self.client.post(self.star_url)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(set(response.data), fields)
                    self.assertEqual(response.data['id'], str(self.experience.pk))
                    self.assertEqual(response.data['is_starred'], expected)
                    self.assertEqual(response.data['star_count'], int(expected))
                    self.assertEqual(self.experience.starred_by.filter(pk=user.pk).exists(), expected)
                    self.assertEqual(self.experience.starred_by.count(), int(expected))
                    self.assertEqual(list(self.other.starred_by.all()), [self.other_reader])
                    self.assertEqual(self.database_snapshot()[0], records_before)
                    self.assertNotIn(user.username, str(response.data))

    def test_star_is_isolated_and_visible_to_list_and_detail(self):
        for user, count in ((self.reader, 1), (self.other_reader, 2)):
            self.client.force_authenticate(user=user)
            response = self.client.post(self.star_url)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data['is_starred'])
            self.assertEqual(response.data['star_count'], count)

        self.client.force_authenticate(user=self.reader)
        unstarred = self.client.post(self.star_url)
        self.assertEqual(unstarred.status_code, 200)
        self.assertFalse(unstarred.data['is_starred'])
        self.assertEqual(unstarred.data['star_count'], 1)
        self.assertEqual(list(self.experience.starred_by.all()), [self.other_reader])

        for user, expected in ((self.reader, False), (self.other_reader, True), (None, False)):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)
                detail = self.client.get(self.detail_url)
                listed = self.client.get(reverse('api:experience-list'))
                self.assertEqual(detail.status_code, 200)
                self.assertEqual(listed.status_code, 200)
                item = next(item for item in listed.data if item['id'] == str(self.experience.pk))
                for data in (detail.data, item):
                    self.assertEqual(data['star_count'], 1)
                    self.assertEqual(data['is_starred'], expected)
                    self.assertNotIn('starred_by', data)
                    self.assertNotIn(self.other_reader.username, str(data))

    def test_payload_cannot_choose_another_user_or_edit_the_record(self):
        self.experience.starred_by.add(self.other_reader)
        self.client.force_authenticate(user=self.reader)
        records_before = self.database_snapshot()[0]
        forged = {
            'user_id': self.other_reader.pk, 'id': str(uuid4()),
            'starred_by': [], 'star_count': 99, 'is_starred': False,
            'title': 'Forged title', 'description_points': ['Forged'],
        }
        for expected, count in ((True, 2), (False, 1)):
            with self.subTest(starred=expected):
                response = self.client.post(self.star_url, forged, format='json')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['id'], str(self.experience.pk))
                self.assertEqual(response.data['is_starred'], expected)
                self.assertEqual(response.data['star_count'], count)
                self.assertTrue(self.experience.starred_by.filter(pk=self.other_reader.pk).exists())
                self.assertEqual(self.experience.starred_by.filter(pk=self.reader.pk).exists(), expected)
                self.assertEqual(self.database_snapshot()[0], records_before)
                self.assertEqual(list(self.other.starred_by.all()), [self.other_reader])

    def test_missing_target_is_404_after_authentication_and_preserves_data(self):
        missing = reverse('api:experience-star', args=[uuid4()])
        before = self.database_snapshot()
        for user, status_code in ((None, 403), (self.reader, 404)):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)
                response = self.client.post(missing)
                self.assertEqual(response.status_code, status_code)
                self.assertIn('detail', response.data)
                self.assertEqual(self.database_snapshot(), before)

    def test_authenticated_wrong_methods_and_options_do_not_toggle(self):
        self.client.force_authenticate(user=self.reader)
        before = self.database_snapshot()
        for method in ('get', 'head', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.star_url)
                self.assertEqual(response.status_code, 405)
                self.assertEqual(self.database_snapshot(), before)

        options = self.client.options(self.star_url)
        self.assertEqual(options.status_code, 200)
        self.assertEqual(set(options['Allow'].replace(' ', '').split(',')), {'POST', 'OPTIONS'})
        self.assertEqual(self.database_snapshot(), before)

    def test_session_toggle_without_csrf_is_rejected_without_changes(self):
        before = self.database_snapshot()
        for user in (self.reader, self.editor, self.owner):
            with self.subTest(user=user.username):
                client, _ = self.session_client_and_token(user)
                response = client.post(self.star_url)
                self.assertEqual(response.status_code, 403)
                self.assertIn('CSRF', str(response.data['detail']))
                self.assertEqual(self.database_snapshot(), before)

    def test_session_toggle_with_wrong_csrf_is_rejected_without_changes(self):
        before = self.database_snapshot()
        for user in (self.reader, self.editor, self.owner):
            with self.subTest(user=user.username):
                client, _ = self.session_client_and_token(user)
                response = client.post(self.star_url, HTTP_X_CSRFTOKEN='invalid')
                self.assertEqual(response.status_code, 403)
                self.assertIn('CSRF', str(response.data['detail']))
                self.assertEqual(self.database_snapshot(), before)

    def test_reader_editor_and_owner_sessions_can_toggle_with_valid_csrf(self):
        for user in (self.reader, self.editor, self.owner):
            client, token = self.session_client_and_token(user)
            for expected in (True, False):
                with self.subTest(user=user.username, starred=expected):
                    response = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.data['is_starred'], expected)
                    self.assertEqual(response.data['star_count'], int(expected))
                    self.assertEqual(self.experience.starred_by.filter(pk=user.pk).exists(), expected)
                    self.assertEqual(list(self.other.starred_by.all()), [self.other_reader])

    def test_new_api_and_legacy_route_share_the_existing_star_relation(self):
        client, token = self.session_client_and_token(self.reader)
        starred = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(starred.status_code, 200)
        self.assertTrue(starred.data['is_starred'])
        legacy = client.post(
            reverse('main:toggle_experience_star', args=[self.experience.pk]),
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(legacy.status_code, 200)
        self.assertFalse(legacy.json()['is_starred'])
        self.assertEqual(legacy.json()['star_count'], 0)
        self.assertFalse(self.experience.starred_by.exists())
        detail = client.get(self.detail_url)
        self.assertFalse(detail.data['is_starred'])
        self.assertEqual(detail.data['star_count'], 0)
        self.assertEqual(Experience.objects.count(), 2)

    def test_expired_session_cannot_toggle_even_with_the_old_csrf_token(self):
        client, token = self.session_client_and_token(self.reader)
        before = self.database_snapshot()
        client.logout()
        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('CSRF', str(response.data['detail']))
        self.assertEqual(self.database_snapshot(), before)
