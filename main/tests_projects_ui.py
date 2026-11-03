from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape

from .models import Project


class ProjectReadPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            title='Portfolio preview',
            project_type='Personal Website',
            role='Developer',
            description='A portfolio with a static preview.',
            technologies='Django\nJavaScript',
            thumbnail_path='img/portfolio.png',
            live_url='https://example.com/',
        )
        cls.other_project = Project.objects.create(
            title='Another project',
            project_type='Web App',
            role='Developer',
            description='Another project.',
            technologies='Python',
            live_url='https://example.com/other/',
        )
        user_model = get_user_model()
        cls.reader = user_model.objects.create_user(username='page-reader')
        cls.editor = user_model.objects.create_user(username='page-editor')
        cls.owner = user_model.objects.create_superuser(username='page-owner')
        editor_group = Group.objects.create(name='Editor')
        editor_group.permissions.add(Permission.objects.get(
            content_type__app_label='main',
            codename='change_project',
        ))
        cls.editor.groups.add(editor_group)
        cls.project.starred_by.add(cls.reader)

    def test_html_fallback_does_not_depend_on_legacy_json(self):
        for url in (reverse('main:show_projects'), self.project.get_absolute_url()):
            with self.subTest(url=url), patch(
                'main.views.get_projects_json',
                side_effect=AssertionError('HTML must not deserialize legacy JSON'),
            ):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, self.project.title)
                self.assertContains(
                    response,
                    f'data-projects-url="{reverse("api:project-list")}"',
                )
                self.assertContains(response, 'id="project-detail-template"')

    def test_empty_database_keeps_the_ajax_containers_available(self):
        Project.objects.all().delete()
        response = self.client.get(reverse('main:show_projects'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No projects have been added yet.')
        self.assertContains(response, 'id="project-index"')
        self.assertContains(response, 'id="project-detail"')
        self.assertContains(response, 'id="project-detail-template"')

    def test_direct_detail_preserves_personal_and_title_filters(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.project.get_absolute_url(), {
            'title': 'preview',
            'starred': 'mine',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_project'].pk, self.project.pk)
        self.assertEqual(
            [project.pk for project in response.context['project_list']],
            [self.project.pk],
        )
        self.assertEqual(response.context['title_query'], 'preview')
        self.assertEqual(response.context['starred_filter'], 'mine')
        self.assertContains(response, f'data-selected-project-id="{self.project.pk}"')
        self.assertContains(response, 'value="preview"')
        self.assertContains(response, 'checked')

    def test_legacy_edit_link_remains_permission_based(self):
        edit_url = reverse('main:update_project', args=[self.project.pk])
        for user, can_edit in (
            (self.reader, False), (self.editor, True), (self.owner, True),
        ):
            with self.subTest(user=str(user)):
                self.client.force_login(user)
                response = self.client.get(self.project.get_absolute_url())

                if can_edit:
                    self.assertContains(response, edit_url)
                else:
                    self.assertNotContains(response, edit_url)

    def test_regular_user_gets_csrf_cookie_without_a_create_modal(self):
        self.client.force_login(self.reader)
        response = self.client.get(reverse('main:show_projects'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('csrftoken', response.cookies)
        self.assertNotContains(response, 'id="project-create-form"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_existing_text_is_escaped_in_the_html_fallback(self):
        self.project.title = '<img src=x onerror=alert(1)>'
        self.project.save(update_fields=['title'])
        response = self.client.get(self.project.get_absolute_url())

        self.assertContains(response, escape(self.project.title))
        self.assertNotContains(response, self.project.title)
