from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from .models import Project
from .permissions import IsPortfolioOwnerOrReadOnly
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


class ProjectPermissionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.reader = user_model.objects.create_user(username='api-reader')
        cls.editor = user_model.objects.create_user(username='api-editor')
        cls.staff = user_model.objects.create_user(
            username='api-staff',
            is_staff=True,
        )
        cls.owner = user_model.objects.create_superuser(username='api-owner')

        editor_group = Group.objects.create(name='Editor')
        editor_group.permissions.add(Permission.objects.get(
            content_type__app_label='main',
            codename='change_project',
        ))
        cls.editor.groups.add(editor_group)

    def is_allowed(self, user, method):
        request = APIRequestFactory().generic(method, '/api/v1/projects/')
        request.user = user

        return IsPortfolioOwnerOrReadOnly().has_permission(request, view=None)

    def test_every_role_can_use_safe_methods(self):
        for user in (
            AnonymousUser(), self.reader, self.editor, self.staff, self.owner,
        ):
            for method in ('GET', 'HEAD', 'OPTIONS'):
                with self.subTest(user=str(user), method=method):
                    self.assertTrue(self.is_allowed(user, method))

    def test_guest_and_regular_user_cannot_write(self):
        for user in (AnonymousUser(), self.reader):
            for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                with self.subTest(user=str(user), method=method):
                    self.assertFalse(self.is_allowed(user, method))

    def test_staff_and_editor_permission_do_not_grant_api_write_access(self):
        self.assertTrue(self.editor.has_perm('main.change_project'))
        self.assertTrue(self.staff.is_staff)

        for user in (self.editor, self.staff):
            self.assertFalse(user.is_superuser)
            for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                with self.subTest(user=str(user), method=method):
                    self.assertFalse(self.is_allowed(user, method))

    def test_superuser_can_write(self):
        for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            with self.subTest(method=method):
                self.assertTrue(self.is_allowed(self.owner, method))


class ProjectListAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.owner = user_model.objects.create_superuser(
            username='list-owner',
            password='test-password',
        )
        cls.reader = user_model.objects.create_user(username='list-reader')
        cls.other_reader = user_model.objects.create_user(username='list-other')
        cls.editor = user_model.objects.create_user(username='list-editor')
        cls.staff = user_model.objects.create_user(
            username='list-staff',
            is_staff=True,
        )
        editor_group = Group.objects.create(name='Editor')
        editor_group.permissions.add(Permission.objects.get(
            content_type__app_label='main',
            codename='change_project',
        ))
        cls.editor.groups.add(editor_group)

        cls.payload = {
            'title': 'Portfolio',
            'project_type': 'Personal Website',
            'role': 'Developer',
            'description': 'My portfolio website.',
            'technologies': 'Django\nJavaScript',
            'live_url': 'https://example.com/',
            'display_order': 2,
        }
        cls.project = Project.objects.create(**cls.payload)
        cls.other_project = Project.objects.create(**{
            **cls.payload,
            'title': 'Another project',
            'display_order': 0,
        })
        cls.project.starred_by.add(cls.reader)
        cls.other_project.starred_by.add(cls.other_reader)

    def setUp(self):
        self.list_url = reverse('api:project-list')

    def test_public_list_is_flat_private_and_ordered_for_every_role(self):
        expected_fields = set(self.payload) | {
            'id', 'thumbnail_path', 'source_url', 'star_count', 'is_starred',
        }

        for user in (
            None, self.reader, self.other_reader, self.editor, self.staff, self.owner,
        ):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)
                response = self.client.get(self.list_url)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item['id'] for item in response.data],
                    [str(self.other_project.pk), str(self.project.pk)],
                )
                for item in response.data:
                    self.assertEqual(set(item), expected_fields)
                    self.assertEqual(item['star_count'], 1)
                    expected_starred = (
                        (user == self.reader and item['id'] == str(self.project.pk))
                        or (
                            user == self.other_reader
                            and item['id'] == str(self.other_project.pk)
                        )
                    )
                    self.assertEqual(item['is_starred'], expected_starred)

    def test_title_search_is_trimmed_case_insensitive_and_can_be_empty(self):
        for title, expected_ids in (
            ('  PORT  ', [str(self.project.pk)]),
            ('not-found', []),
        ):
            with self.subTest(title=title):
                response = self.client.get(self.list_url, {'title': title})

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item['id'] for item in response.data], expected_ids,
                )

    def test_personal_filter_is_isolated_and_combines_with_search(self):
        for user, title, expected_ids in (
            (None, '', []),
            (self.reader, '', [str(self.project.pk)]),
            (self.other_reader, '', [str(self.other_project.pk)]),
            (self.reader, 'PORT', [str(self.project.pk)]),
            (self.reader, 'Another', []),
        ):
            with self.subTest(user=str(user), title=title):
                self.client.force_authenticate(user=user)
                response = self.client.get(self.list_url, {
                    'starred': 'mine',
                    'title': title,
                })

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item['id'] for item in response.data], expected_ids,
                )

    def test_owner_can_create_a_project_with_cleaned_text(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload,
            'title': '<b>New portfolio</b>',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(pk=response.data['id'])
        self.assertEqual(project.title, 'New portfolio')
        self.assertEqual(project.technologies, self.payload['technologies'])
        self.assertEqual(project.starred_by.count(), 0)
        self.assertEqual(Project.objects.count(), 3)

    def test_invalid_create_returns_field_errors_without_saving(self):
        self.client.force_authenticate(user=self.owner)

        for changes, field in (
            ({'title': '   '}, 'title'),
            ({'title': '<img src="x" onerror="alert(1)">'}, 'title'),
            ({'live_url': 'javascript:alert(1)'}, 'live_url'),
            ({'display_order': -1}, 'display_order'),
        ):
            with self.subTest(field=field, changes=changes):
                response = self.client.post(self.list_url, {
                    **self.payload,
                    **changes,
                }, format='json')

                self.assertEqual(response.status_code, 400)
                self.assertIsInstance(response.data[field], list)
                self.assertEqual(Project.objects.count(), 2)

    def test_nonowners_cannot_create_or_change_existing_data(self):
        projects_before = list(Project.objects.values())
        stars_before = list(Project.starred_by.through.objects.values())

        for user in (None, self.reader, self.editor, self.staff):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)
                response = self.client.post(
                    self.list_url, self.payload, format='json',
                )

                self.assertEqual(response.status_code, 403)
                self.assertIn('detail', response.data)
                self.assertEqual(list(Project.objects.values()), projects_before)
                self.assertEqual(
                    list(Project.starred_by.through.objects.values()), stars_before,
                )

    def test_create_ignores_forged_id_and_star_fields(self):
        self.client.force_authenticate(user=self.owner)
        forged_id = uuid4()
        response = self.client.post(self.list_url, {
            **self.payload,
            'id': str(forged_id),
            'star_count': 99,
            'is_starred': True,
            'starred_by': [self.reader.pk],
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data['id'], str(forged_id))
        self.assertEqual(response.data['star_count'], 0)
        self.assertFalse(response.data['is_starred'])
        self.assertFalse(Project.objects.filter(pk=forged_id).exists())
        self.assertFalse(
            Project.objects.get(pk=response.data['id']).starred_by.exists(),
        )

    def test_unsupported_list_methods_are_rejected_without_mutation(self):
        self.client.force_authenticate(user=self.owner)

        for method in ('put', 'patch', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.list_url)

                self.assertEqual(response.status_code, 405)
                self.assertEqual(Project.objects.count(), 2)
                self.project.refresh_from_db()
                self.assertEqual(self.project.title, self.payload['title'])

    def test_malformed_json_is_rejected_without_saving(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            data='{"title":',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Project.objects.count(), 2)

    def test_head_and_options_are_read_only(self):
        head = self.client.head(self.list_url)
        options = self.client.options(self.list_url)

        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.content, b'')
        self.assertEqual(options.status_code, 200)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(self.project.starred_by.count(), 1)

    def test_browsable_api_is_available(self):
        response = self.client.get(self.list_url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.accepted_renderer.format, 'api')
        self.assertContains(response, reverse('rest_framework:login'))

    def test_session_create_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(
            username='list-owner', password='test-password',
        ))
        response = client.post(self.list_url, self.payload, format='json')

        self.assertEqual(response.status_code, 403)
        self.assertIn('CSRF', str(response.data['detail']))
        self.assertEqual(Project.objects.count(), 2)

    def test_session_create_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(
            username='list-owner', password='test-password',
        ))
        page = client.get(self.list_url, HTTP_ACCEPT='text/html')
        self.assertEqual(page.status_code, 200)
        token = client.cookies['csrftoken'].value

        response = client.post(
            self.list_url,
            self.payload,
            format='json',
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(pk=response.data['id']).exists())
        self.assertEqual(Project.objects.count(), 3)
