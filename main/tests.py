from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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
        response = self.client.get(reverse('main:show_projects'))

        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.project_type)
        self.assertContains(response, self.project.role)
        self.assertContains(response, self.project.description)

        for technology in self.project.technology_list:
            self.assertContains(response, technology)

    def test_empty_projects_page(self):
        Project.objects.all().delete()

        response = self.client.get(reverse('main:show_projects'))

        self.assertContains(
            response,
            'No projects have been added yet.',
        )
        self.assertNotContains(response, self.project.title)
