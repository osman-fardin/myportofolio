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
        self.project = Project.objects.create(
            title='Portfolio',
            project_type='Personal Website',
            role='Developer',
            description='My portfolio website.',
            technologies='Django\nJavaScript',
            live_url='https://example.com/',
        )
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
