from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory, APITestCase

from .models import Project
from .serializers import ProjectSerializer


class ProjectSerializerTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='project-reader',
        )
        self.payload = {
            'title': 'Portfolio',
            'project_type': 'Personal Website',
            'role': 'Developer',
            'description': 'My portfolio website.',
            'technologies': 'Django\nJavaScript',
            'live_url': 'https://example.com/',
        }
        self.project = Project.objects.create(**self.payload)
        self.project.starred_by.add(self.user)

    def test_public_data_without_request_hides_star_accounts(self):
        data = ProjectSerializer(self.project).data

        self.assertEqual(data['id'], str(self.project.pk))
        self.assertEqual(data['star_count'], 1)
        self.assertFalse(data['is_starred'])
        self.assertNotIn('starred_by', data)
        self.assertNotIn('starred_by_names', data)
        self.assertNotIn(self.user.username, str(data))

    def test_star_status_follows_the_current_user(self):
        other_user = get_user_model().objects.create_user(
            username='other-reader',
        )
        factory = APIRequestFactory()

        for user, expected in [
            (self.user, True),
            (other_user, False),
            (AnonymousUser(), False),
        ]:
            with self.subTest(user=str(user)):
                request = factory.get('/api/v1/projects/')
                request.user = user

                data = ProjectSerializer(
                    self.project,
                    context={'request': request},
                ).data

                self.assertEqual(data['star_count'], 1)
                self.assertEqual(data['is_starred'], expected)

    def test_client_cannot_overwrite_id_or_star_metadata(self):
        original_id = self.project.pk

        serializer = ProjectSerializer(
            self.project,
            data={
                'id': str(uuid4()),
                'star_count': 99,
                'is_starred': False,
                'starred_by': [],
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data, {})

        serializer.save()
        self.project.refresh_from_db()

        self.assertEqual(self.project.pk, original_id)
        self.assertEqual(
            list(self.project.starred_by.values_list('pk', flat=True)),
            [self.user.pk],
        )
        self.assertEqual(Project.objects.count(), 1)

    def test_text_is_cleaned_before_a_project_is_saved(self):
        expected = {
            'title': 'Portfolio',
            'project_type': 'Personal Website',
            'role': 'Developer',
            'description': 'My portfolio website.',
            'technologies': 'Django\nJavaScript',
            'thumbnail_path': 'img/portfolio.png',
        }
        serializer = ProjectSerializer(data={
            **self.payload,
            'title': ' <b>Portfolio</b> ',
            'project_type': '<em>Personal Website</em>',
            'role': '<strong>Developer</strong>',
            'description': '<p>My portfolio website.</p>',
            'technologies': '<b>Django</b>\n<i>JavaScript</i>',
            'thumbnail_path': ' <span>img/portfolio.png</span> ',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        project = serializer.save()
        project.refresh_from_db()

        for field, value in expected.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(project, field), value)

    def test_required_text_cannot_be_blank_or_only_html(self):
        for field in (
            'title', 'project_type', 'role', 'description', 'technologies',
        ):
            for value in ('', '   ', '<img src="x" onerror="alert(1)">'):
                with self.subTest(field=field, value=value):
                    serializer = ProjectSerializer(data={
                        **self.payload,
                        field: value,
                    })

                    self.assertFalse(serializer.is_valid())
                    self.assertIn(field, serializer.errors)

        self.assertEqual(Project.objects.count(), 1)

    def test_invalid_urls_are_rejected(self):
        for field in ('live_url', 'source_url'):
            for value in ('javascript:alert(1)', 'not-a-url'):
                with self.subTest(field=field, value=value):
                    serializer = ProjectSerializer(data={
                        **self.payload,
                        field: value,
                    })

                    self.assertFalse(serializer.is_valid())
                    self.assertIn(field, serializer.errors)

        self.assertEqual(Project.objects.count(), 1)

    def test_optional_fields_keep_the_model_defaults(self):
        serializer = ProjectSerializer(data=self.payload)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        project = serializer.save()
        project.refresh_from_db()

        self.assertEqual(project.thumbnail_path, '')
        self.assertEqual(project.source_url, '')
        self.assertEqual(project.display_order, 0)

    def test_model_field_limits_are_enforced(self):
        for field, value in (
            ('title', 'a' * 201),
            ('project_type', 'a' * 101),
            ('role', 'a' * 101),
            ('thumbnail_path', 'a' * 256),
            ('display_order', -1),
        ):
            with self.subTest(field=field):
                serializer = ProjectSerializer(data={
                    **self.payload,
                    field: value,
                })

                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

        self.assertEqual(Project.objects.count(), 1)

    def test_partial_update_cleans_text_and_preserves_other_data(self):
        serializer = ProjectSerializer(
            self.project,
            data={'title': '<b>Updated portfolio</b>'},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.project.refresh_from_db()

        self.assertEqual(self.project.title, 'Updated portfolio')
        for field in ('description', 'technologies', 'live_url'):
            with self.subTest(field=field):
                self.assertEqual(getattr(self.project, field), self.payload[field])
        self.assertTrue(self.project.starred_by.filter(pk=self.user.pk).exists())
        self.assertEqual(Project.objects.count(), 1)

    def test_full_update_requires_all_required_fields(self):
        serializer = ProjectSerializer(
            self.project,
            data={'title': 'Incomplete replacement'},
        )

        self.assertFalse(serializer.is_valid())
        for field in (
            'project_type', 'role', 'description', 'technologies', 'live_url',
        ):
            with self.subTest(field=field):
                self.assertIn(field, serializer.errors)

        self.project.refresh_from_db()
        self.assertEqual(self.project.title, self.payload['title'])
