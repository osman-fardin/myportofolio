from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory, APITestCase

from .models import Experience
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
