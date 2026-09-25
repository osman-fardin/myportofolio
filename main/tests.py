import json
import uuid
from datetime import timedelta

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ExperienceForm
from .models import Experience, Project



class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title='Teaching Assistant, Programming Foundations 1',
            description=(
                'Assist students through weekly lab support.'
                '\n'
                'Guide students through introductory Python assignments.'
            ),
            category='part-time',
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse('main:show_main'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertNotContains(response, self.experience.title)

        experience_url = reverse('main:show_experience')
        self.assertContains(response, f'href="{experience_url}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get('/halaman-yang-tidak-ada/')

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(
            str(self.experience),
            'Teaching Assistant, Programming Foundations 1',
        )
        self.assertEqual(self.experience.category, 'part-time')
        self.assertTrue(self.experience.is_ongoing)
        self.assertEqual(
            self.experience.description_points,
            [
                'Assist students through weekly lab support.',
                'Guide students through introductory Python assignments.',
            ],
        )

    def test_experience_page(self):
        response = self.client.get(reverse('main:show_experience'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experience.html')
        self.assertContains(response, self.experience.title)

        for point in self.experience.description_points:
            self.assertContains(response, point)

        self.assertContains(
            response,
            self.experience.get_category_display(),
        )
        self.assertContains(response, 'Present')

        main_url = reverse('main:show_main')
        self.assertContains(response, f'href="{main_url}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()

        response = self.client.get(reverse('main:show_experience'))

        self.assertContains(
            response,
            'No experience has been added yet.',
        )
        self.assertNotContains(response, self.experience.title)

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        response = self.client.get(reverse('main:show_experience'))

        self.assertFalse(self.experience.is_ongoing)
        self.assertNotContains(response, 'Present')

        completed_month = timezone.localtime(
            self.experience.ended_at
        ).strftime('%b %Y')
        self.assertContains(response, completed_month)


class ExperienceFormTests(TestCase):
    def setUp(self):
        self.started_at = timezone.now()
        self.valid_data = {
            'title': 'Cloud Security Intern',
            'description': 'Reviewed cloud security configurations.',
            'category': 'internship',
            'thumbnail': '',
            'started_at': self.started_at,
            'ended_at': '',
        }

    def test_form_contains_expected_fields_and_excludes_uuid(self):
        form = ExperienceForm()

        self.assertEqual(
            list(form.fields),
            [
                'title',
                'description',
                'category',
                'thumbnail',
                'started_at',
                'ended_at',
            ],
        )
        self.assertNotIn('id', form.fields)

    def test_end_date_before_start_date_is_rejected(self):
        invalid_data = self.valid_data.copy()
        invalid_data['ended_at'] = (
            self.started_at - timedelta(days=1)
        )

        form = ExperienceForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('ended_at', form.errors)
        self.assertIn(
            'End date cannot be earlier than start date.',
            form.errors['ended_at'],
        )


class ExperienceCrudTests(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title='Teaching Assistant',
            description='Guide students through programming exercises.',
            category='part-time',
        )

    def _form_data(self, **overrides):
        data = {
            'title': 'Cloud Security Intern',
            'description': 'Reviewed cloud security configurations.',
            'category': 'internship',
            'thumbnail': '',
            'started_at': '2026-09-19T10:00',
            'ended_at': '',
        }
        data.update(overrides)

        return data

    def test_create_get_renders_shared_form(self):
        response = self.client.get(
            reverse('main:create_experience')
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'experience_form.html',
        )
        self.assertIsInstance(
            response.context['form'],
            ExperienceForm,
        )
        self.assertContains(response, 'Add experience')

    def test_valid_create_post_saves_and_redirects(self):
        count_before = Experience.objects.count()

        response = self.client.post(
            reverse('main:create_experience'),
            self._form_data(),
        )

        self.assertRedirects(
            response,
            reverse('main:show_experience'),
        )
        self.assertEqual(
            Experience.objects.count(),
            count_before + 1,
        )

        created_experience = Experience.objects.get(
            title='Cloud Security Intern'
        )
        self.assertEqual(
            created_experience.category,
            'internship',
        )

    def test_update_get_prefills_selected_experience(self):
        response = self.client.get(
            reverse(
                'main:update_experience',
                kwargs={
                    'experience_id': self.experience.id,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'experience_form.html',
        )
        self.assertEqual(
            response.context['form'].instance,
            self.experience,
        )
        self.assertContains(response, self.experience.title)

    def test_valid_update_post_changes_selected_object(self):
        response = self.client.post(
            reverse(
                'main:update_experience',
                kwargs={
                    'experience_id': self.experience.id,
                },
            ),
            self._form_data(
                title='Updated Teaching Assistant',
                category='volunteer',
            ),
        )

        self.assertRedirects(
            response,
            reverse('main:show_experience'),
        )

        self.experience.refresh_from_db()

        self.assertEqual(
            self.experience.title,
            'Updated Teaching Assistant',
        )
        self.assertEqual(
            self.experience.category,
            'volunteer',
        )
        self.assertEqual(Experience.objects.count(), 1)

    def test_missing_update_returns_404(self):
        response = self.client.get(
            reverse(
                'main:update_experience',
                kwargs={
                    'experience_id': uuid.uuid4(),
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_get_is_rejected_and_preserves_object(self):
        delete_url = reverse(
            'main:delete_experience',
            kwargs={
                'experience_id': self.experience.id,
            },
        )

        response = self.client.get(delete_url)

        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            Experience.objects.filter(
                id=self.experience.id,
            ).exists()
        )

    def test_delete_post_removes_object_and_redirects(self):
        experience_id = self.experience.id
        delete_url = reverse(
            'main:delete_experience',
            kwargs={
                'experience_id': experience_id,
            },
        )

        response = self.client.post(delete_url)

        self.assertRedirects(
            response,
            reverse('main:show_experience'),
        )
        self.assertFalse(
            Experience.objects.filter(
                id=experience_id,
            ).exists()
        )

class ExperienceJsonTests(TestCase):
    def setUp(self):
        self.ongoing_experience = Experience.objects.create(
            title='Teaching Assistant',
            description='Guide students through programming exercises.',
            category='part-time',
        )
        self.completed_experience = Experience.objects.create(
            title='Academic Mentor',
            description='Mentored beginner programmers.',
            category='volunteer',
            ended_at=timezone.now(),
        )

    def _get_json(self, params=None):
        response = self.client.get(
            reverse('main:get_experiences_json'),
            params or {},
        )

        return response, json.loads(response.content)

    def test_json_endpoint_returns_valid_experience_data(self):
        response, data = self._get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/json',
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(
            {item['pk'] for item in data},
            {
                str(self.ongoing_experience.id),
                str(self.completed_experience.id),
            },
        )

    def test_json_filters_return_matching_experiences(self):
        cases = [
            (
                'title',
                {'title': 'assistant'},
                {str(self.ongoing_experience.id)},
            ),
            (
                'category',
                {'category': 'volunteer'},
                {str(self.completed_experience.id)},
            ),
            (
                'ongoing',
                {'status': 'ongoing'},
                {str(self.ongoing_experience.id)},
            ),
            (
                'completed',
                {'status': 'completed'},
                {str(self.completed_experience.id)},
            ),
            (
                'combined',
                {
                    'title': 'teaching',
                    'category': 'part-time',
                    'status': 'ongoing',
                },
                {str(self.ongoing_experience.id)},
            ),
        ]

        for case_name, params, expected_ids in cases:
            with self.subTest(case=case_name):
                _, data = self._get_json(params)
                actual_ids = {
                    item['pk']
                    for item in data
                }

                self.assertEqual(actual_ids, expected_ids)

    def test_experience_page_renders_deserialized_objects(self):
        response = self.client.get(
            reverse('main:show_experience'),
            {'status': 'ongoing'},
        )

        experience_list = response.context['experience_list']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(experience_list), 1)
        self.assertIsInstance(
            experience_list[0],
            Experience,
        )
        self.assertEqual(
            experience_list[0].id,
            self.ongoing_experience.id,
        )
        self.assertContains(
            response,
            self.ongoing_experience.title,
        )
        self.assertNotContains(
            response,
            self.completed_experience.title,
        )

        no_match_response = self.client.get(
            reverse('main:show_experience'),
            {'title': 'definitely-not-found'},
        )
        self.assertContains(
            no_match_response,
            'No experiences match the selected filters.',
        )


class ProjectPageTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='Fasilkom Study Hub',
            project_type='Community Study Platform',
            role='Creator and Developer',
            description=(
                'A study platform that helps Fasilkom students '
                'organize courses and learning resources.'
            ),
            technologies='Next.js\nTypeScript\nCloudflare',
            thumbnail_path='img/fasilkom-study-hub-semester.jpg',
            live_url='https://fasilkom-study-hub.pages.dev/',
            source_url='https://github.com/osman-fardin/fasilkom-study-hub',
            display_order=1,
        )

    def test_projects_page_is_accessible(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects.html')

    def test_project_data_appears_on_page(self):
        response = self.client.get(self.project.get_absolute_url())

        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.project_type)
        self.assertContains(response, self.project.role)
        self.assertContains(response, self.project.description)

        for technology in self.project.technology_list:
            self.assertContains(response, technology)

        self.assertContains(response, 'aria-current="page"')

    def test_empty_projects_page(self):
        Project.objects.all().delete()

        response = self.client.get(reverse('main:show_projects'))

        self.assertContains(
            response,
            'No projects have been added yet.',
        )
        self.assertNotContains(response, self.project.title)

    def test_project_detail_uses_uuid_route(self):
        self.assertEqual(
            self.project.get_absolute_url(),
            reverse(
                'main:show_project_detail',
                kwargs={'project_id': self.project.id},
            ),
        )

    def test_missing_project_detail_returns_404(self):
        response = self.client.get(
            reverse(
                'main:show_project_detail',
                kwargs={'project_id': uuid.uuid4()},
            )
        )

        self.assertEqual(response.status_code, 404)


class ProjectAccessTests(TestCase):
    def test_guest_is_redirected_from_create_form(self):
        url = reverse('main:create_project')

        response = self.client.get(url)

        self.assertRedirects(
            response,
            f"{reverse('main:login')}?next={url}",
            fetch_redirect_response=False,
        )

    def test_regular_user_cannot_open_create_form(self):
        user = get_user_model().objects.create_user(
            username='regular_user',
            password='test-password',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('main:create_project'))

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_open_create_form(self):
        admin = get_user_model().objects.create_superuser(
            username='portfolio_owner',
            email='owner@example.com',
            password='test-password',
        )
        self.client.force_login(admin)

        response = self.client.get(reverse('main:create_project'))

        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_delete_project(self):
        project = Project.objects.create(
            title='Protected Project',
            project_type='Web App',
            role='Developer',
            description='This project must remain.',
            technologies='Django',
            live_url='https://example.com/',
        )
        user = get_user_model().objects.create_user(
            username='regular_user',
            password='test-password',
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('main:delete_project', args=[project.id])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=project.pk).exists())

    def test_superuser_can_delete_project(self):
        project = Project.objects.create(
            title='Project to Delete',
            project_type='Web App',
            role='Developer',
            description='Temporary test project.',
            technologies='Django',
            live_url='https://example.com/',
        )
        admin = get_user_model().objects.create_superuser(
            username='portfolio_owner',
            email='owner@example.com',
            password='test-password',
        )
        self.client.force_login(admin)

        response = self.client.post(
            reverse('main:delete_project', args=[project.id])
        )

        self.assertRedirects(response, reverse('main:show_projects'))
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())


class ProjectUpdatePermissionTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='Editable Project',
            project_type='Web App',
            role='Developer',
            description='Original description.',
            technologies='Django',
            live_url='https://example.com/',
        )
        self.update_url = reverse(
            'main:update_project',
            args=[self.project.id],
        )

        user_model = get_user_model()

        self.regular_user = user_model.objects.create_user(
            username='regular_user',
            password='test-password',
        )
        self.editor = user_model.objects.create_user(
            username='project_editor',
            password='test-password',
        )
        self.superuser = user_model.objects.create_superuser(
            username='portfolio_owner',
            email='owner@example.com',
            password='test-password',
        )

        editor_group = Group.objects.create(name='Editor')
        change_permission = Permission.objects.get(
            content_type__app_label='main',
            codename='change_project',
        )
        editor_group.permissions.add(change_permission)
        self.editor.groups.add(editor_group)

    def test_guest_is_redirected_from_update_form(self):
        response = self.client.get(self.update_url)

        self.assertRedirects(
            response,
            f"{reverse('main:login')}?next={self.update_url}",
            fetch_redirect_response=False,
        )

    def test_regular_user_cannot_open_update_form(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(self.update_url)

        self.assertEqual(response.status_code, 403)

    def test_editor_can_open_update_form(self):
        self.client.force_login(self.editor)

        response = self.client.get(self.update_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit project')
        self.assertContains(response, self.project.title)

    def test_superuser_can_open_update_form(self):
        self.client.force_login(self.superuser)

        response = self.client.get(self.update_url)

        self.assertEqual(response.status_code, 200)

    def test_editor_can_update_project(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            self.update_url,
            {
                'title': 'Updated Project',
                'project_type': 'Web Platform',
                'role': 'Lead Developer',
                'description': 'Updated description.',
                'technologies': 'Django\nPostgreSQL',
                'thumbnail_path': '',
                'live_url': 'https://example.com/updated/',
                'source_url': '',
                'display_order': 1,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                'main:show_project_detail',
                args=[self.project.id],
            ),
        )

        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Updated Project')
        self.assertEqual(self.project.role, 'Lead Developer')


    def test_editor_cannot_create_or_delete_project(self):
        self.client.force_login(self.editor)

        create_response = self.client.get(
            reverse('main:create_project')
        )
        delete_response = self.client.post(
            reverse(
                'main:delete_project',
                args=[self.project.id],
            )
        )

        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
        self.assertTrue(
            Project.objects.filter(pk=self.project.pk).exists()
        )


    def test_edit_link_follows_change_permission(self):
        detail_url = self.project.get_absolute_url()

        self.client.force_login(self.regular_user)
        regular_response = self.client.get(detail_url)
        self.assertNotContains(regular_response, self.update_url)

        self.client.force_login(self.editor)
        editor_response = self.client.get(detail_url)
        self.assertContains(editor_response, self.update_url)


class ProjectStarTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='Fasilkom Study Hub',
            project_type='Web App',
            role='Developer',
            description='Study resources for students.',
            technologies='Django',
            live_url='https://example.com/',
        )
        user_model = get_user_model()
        self.alice = user_model.objects.create_user(
            username='alice',
            password='test-password',
        )
        self.bob = user_model.objects.create_user(
            username='bob',
            password='test-password',
        )
        self.star_url = reverse(
            'main:toggle_project_star',
            args=[self.project.id],
        )
        self.detail_url = self.project.get_absolute_url()

    def test_guest_cannot_star_project(self):
        response = self.client.post(self.star_url)

        self.assertRedirects(
            response,
            f"{reverse('main:login')}?next={self.star_url}",
            fetch_redirect_response=False,
        )
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_get_does_not_change_stars(self):
        self.client.force_login(self.alice)

        response = self.client.get(self.star_url)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_post_toggles_star_and_button_state(self):
        self.client.force_login(self.alice)

        response = self.client.post(self.star_url)

        self.assertRedirects(response, self.detail_url)
        self.assertTrue(
            self.project.starred_by.filter(pk=self.alice.pk).exists()
        )
        self.assertContains(
            self.client.get(self.detail_url),
            'aria-pressed="true"',
        )

        response = self.client.post(self.star_url)

        self.assertRedirects(response, self.detail_url)
        self.assertEqual(self.project.starred_by.count(), 0)
        self.assertContains(
            self.client.get(self.detail_url),
            'aria-pressed="false"',
        )

    def test_stars_are_independent_per_user(self):
        self.client.force_login(self.alice)
        self.client.post(self.star_url)

        self.client.force_login(self.bob)
        self.assertContains(
            self.client.get(self.detail_url),
            'aria-pressed="false"',
        )
        self.client.post(self.star_url)
        self.assertEqual(self.project.starred_by.count(), 2)

        self.client.force_login(self.alice)
        self.client.post(self.star_url)

        self.assertFalse(
            self.project.starred_by.filter(pk=self.alice.pk).exists()
        )
        self.assertTrue(
            self.project.starred_by.filter(pk=self.bob.pk).exists()
        )
        self.assertEqual(self.project.starred_by.count(), 1)

    def test_project_api_hides_starred_user_identities(self):
        self.project.starred_by.add(self.alice, self.bob)

        response = self.client.get(
            reverse('main:get_projects_json')
        )
        projects = json.loads(response.content)
        project_fields = projects[0]['fields']

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('starred_by', project_fields)


class PersonalStarredProjectFilterTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.alice = user_model.objects.create_user(
            username='alice_filter',
            password='test-password',
        )
        self.bob = user_model.objects.create_user(
            username='bob_filter',
            password='test-password',
        )

        self.cloud_project = Project.objects.create(
            title='Cloud Security Dashboard',
            project_type='Web App',
            role='Developer',
            description='Cloud security monitoring.',
            technologies='Django',
            live_url='https://example.com/cloud/',
        )
        self.study_project = Project.objects.create(
            title='Student Study Hub',
            project_type='Web App',
            role='Developer',
            description='Student learning resources.',
            technologies='Django',
            live_url='https://example.com/study/',
        )
        self.bob_project = Project.objects.create(
            title='Bob Personal Project',
            project_type='Web App',
            role='Developer',
            description='A project starred only by Bob.',
            technologies='Django',
            live_url='https://example.com/bob/',
        )

        self.cloud_project.starred_by.add(self.alice)
        self.study_project.starred_by.add(self.alice)
        self.bob_project.starred_by.add(self.bob)

        self.projects_url = reverse('main:show_projects')

    def test_user_sees_only_personal_starred_projects(self):
        self.client.force_login(self.alice)

        response = self.client.get(
            self.projects_url,
            {'starred': 'mine'},
        )
        project_ids = {
            project.id
            for project in response.context['project_list']
        }

        self.assertSetEqual(
            project_ids,
            {
                self.cloud_project.id,
                self.study_project.id,
            },
        )
        self.assertNotIn(self.bob_project.id, project_ids)

    def test_personal_filter_combines_with_title_search(self):
        self.client.force_login(self.alice)

        response = self.client.get(
            self.projects_url,
            {
                'starred': 'mine',
                'title': 'cloud',
            },
        )
        projects = response.context['project_list']

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].id, self.cloud_project.id)

    def test_personal_filter_is_isolated_between_users(self):
        self.client.force_login(self.bob)

        response = self.client.get(
            self.projects_url,
            {'starred': 'mine'},
        )
        project_ids = {
            project.id
            for project in response.context['project_list']
        }

        self.assertSetEqual(
            project_ids,
            {self.bob_project.id},
        )

    def test_guest_cannot_view_a_personal_collection(self):
        response = self.client.get(
            self.projects_url,
            {'starred': 'mine'},
        )

        self.assertEqual(response.context['project_list'], [])
        self.assertNotContains(response, 'name="starred"')

    def test_empty_personal_collection_has_clear_feedback(self):
        self.client.force_login(self.alice)
        self.cloud_project.starred_by.remove(self.alice)
        self.study_project.starred_by.remove(self.alice)

        response = self.client.get(
            self.projects_url,
            {'starred': 'mine'},
        )

        self.assertContains(
            response,
            'You have not starred any projects yet.',
        )
        self.assertContains(response, 'checked')


class ProjectApiPrivacyTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='Cloud Security Dashboard',
            project_type='Web App',
            role='Developer',
            description='A security monitoring dashboard.',
            technologies='Django\nPostgreSQL',
            live_url='https://example.com/cloud/',
        )
        self.other_project = Project.objects.create(
            title='Student Study Hub',
            project_type='Web App',
            role='Developer',
            description='A study resource platform.',
            technologies='Django',
            live_url='https://example.com/study/',
        )
        self.user = get_user_model().objects.create_user(
            username='private_user',
            email='private@example.com',
            password='private-password',
        )
        self.project.starred_by.add(self.user)
        self.api_url = reverse('main:get_projects_json')

    def test_project_api_only_contains_public_fields(self):
        response = self.client.get(self.api_url)
        projects = response.json()

        expected_fields = {
            'title',
            'project_type',
            'role',
            'description',
            'technologies',
            'thumbnail_path',
            'live_url',
            'source_url',
            'display_order',
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers['Content-Type'],
            'application/json',
        )
        self.assertEqual(
            set(projects[0]['fields']),
            expected_fields,
        )

    def test_project_api_does_not_expose_account_data(self):
        response = self.client.get(self.api_url)

        self.assertNotContains(response, 'starred_by')
        self.assertNotContains(response, self.user.username)
        self.assertNotContains(response, self.user.email)
        self.assertNotContains(response, 'private-password')

    def test_project_api_keeps_title_filter(self):
        response = self.client.get(
            self.api_url,
            {'title': 'cloud'},
        )
        projects = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 1)
        self.assertEqual(
            projects[0]['fields']['title'],
            self.project.title,
        )


class AuthenticationCookieTests(TestCase):
    def test_login_sets_and_logout_deletes_last_login_cookie(self):
        get_user_model().objects.create_user(
            username='cookie_user',
            password='test-password',
        )

        login_response = self.client.post(
            reverse('main:login'),
            {
                'username': 'cookie_user',
                'password': 'test-password',
            },
        )

        self.assertRedirects(login_response, reverse('main:show_main'))
        last_login = login_response.cookies['last_login'].value
        self.assertRegex(
            last_login,
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
        )
        self.assertEqual(
            self.client.get(reverse('main:show_main')).context['last_login'],
            last_login,
        )

        logout_response = self.client.get(reverse('main:logout'))

        self.assertRedirects(logout_response, reverse('main:show_main'))
        self.assertEqual(logout_response.cookies['last_login'].value, '')
        self.assertEqual(
            logout_response.cookies['last_login']['max-age'],
            0,
        )
        self.assertEqual(
            self.client.get(reverse('main:show_main')).context['last_login'],
            'No login session recorded',
        )
