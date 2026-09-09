from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Experience


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