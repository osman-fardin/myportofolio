import json
import uuid
from datetime import timedelta

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
