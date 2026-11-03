from html.parser import HTMLParser
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from rest_framework.test import APIClient

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


class _ProjectCreateFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.form_attributes = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'form' and attributes.get('id') == 'project-create-form':
            self.form_attributes = attributes


class ProjectCreatePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser(
            username='create-page-owner',
            password='test-password',
        )
        cls.payload = {
            'title': 'Portfolio create test',
            'project_type': 'Personal Website',
            'role': 'Developer',
            'description': 'Created from the portfolio modal.',
            'technologies': 'Django\nJavaScript',
            'thumbnail_path': '',
            'live_url': 'https://example.com/',
            'source_url': '',
            'display_order': '0',
        }

    def _client_and_form(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(
            username='create-page-owner', password='test-password',
        ))
        page = client.get(reverse('main:show_projects'))
        self.assertEqual(page.status_code, 200)
        parser = _ProjectCreateFormParser()
        parser.feed(page.content.decode())
        self.assertTrue(parser.form_attributes)

        return client, parser.form_attributes, client.cookies['csrftoken'].value

    def test_modal_targets_support_json_create_and_html_fallback(self):
        client, form, token = self._client_and_form()
        self.assertEqual(form['data-api-url'], reverse('api:project-list'))
        self.assertEqual(form['action'], reverse('main:create_project'))

        api = client.post(
            form['data-api-url'], self.payload, format='json',
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(api.status_code, 201)
        project = Project.objects.get(pk=api.data['id'])
        self.assertEqual(project.title, self.payload['title'])
        self.assertEqual(project.technologies, self.payload['technologies'])
        self.assertEqual(project.display_order, 0)

        fallback = client.post(form['action'], {
            **self.payload,
            'title': 'HTML fallback project',
        }, HTTP_X_CSRFTOKEN=token)
        self.assertRedirects(
            fallback, reverse('main:show_projects'), fetch_redirect_response=False,
        )
        self.assertTrue(Project.objects.filter(title='HTML fallback project').exists())
        self.assertEqual(Project.objects.count(), 2)

    def test_invalid_json_create_from_the_page_does_not_save(self):
        client, form, token = self._client_and_form()
        response = client.post(form['data-api-url'], {
            **self.payload,
            'title': '<img src="x" onerror="alert(1)">',
        }, format='json', HTTP_X_CSRFTOKEN=token)

        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)
        self.assertEqual(Project.objects.count(), 0)

    def test_session_expiry_rejects_create_without_saving(self):
        client, form, token = self._client_and_form()
        client.logout()
        response = client.post(
            form['data-api-url'], self.payload, format='json',
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn('detail', response.data)
        self.assertEqual(Project.objects.count(), 0)


class _ProjectStarFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'form' and 'project-star-form' in attributes.get('class', '').split():
            self.forms.append(attributes)


class ProjectStarPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            title='Star from the project viewer',
            project_type='Web App',
            role='Developer',
            description='A project with a star form.',
            technologies='Django',
            live_url='https://example.com/',
        )
        user_model = get_user_model()
        cls.reader = user_model.objects.create_user(
            username='star-page-reader', password='test-password',
        )
        cls.editor = user_model.objects.create_user(
            username='star-page-editor', password='test-password',
        )
        cls.editor.user_permissions.add(Permission.objects.get(
            content_type__app_label='main', codename='change_project',
        ))
        cls.owner = user_model.objects.create_superuser(
            username='star-page-owner', password='test-password',
        )

    def _client_and_form(self, user):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=user.username, password='test-password'))
        page = client.get(self.project.get_absolute_url())
        parser = _ProjectStarFormParser()
        parser.feed(page.content.decode())
        self.assertEqual(len(parser.forms), 2)  # Selected detail and the inert template.
        self.assertEqual(
            parser.forms[0]['data-api-url'],
            reverse('api:project-star', args=[self.project.pk]),
        )
        self.assertIn(
            '00000000-0000-0000-0000-000000000000',
            parser.forms[1]['data-api-url'],
        )
        return client, parser.forms[0], client.cookies['csrftoken'].value

    def test_each_authenticated_role_can_toggle_using_the_page_api_url(self):
        for user in (self.reader, self.editor, self.owner):
            with self.subTest(user=user.username):
                client, form, token = self._client_and_form(user)
                for expected in (True, False):
                    response = client.post(form['data-api-url'], HTTP_X_CSRFTOKEN=token)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.data['is_starred'], expected)
                    self.assertEqual(response.data['star_count'], int(expected))
                    self.assertEqual(self.project.starred_by.filter(pk=user.pk).exists(), expected)
                    self.assertNotIn('starred_by', response.data)

    def test_html_fallback_still_toggles_the_same_relation(self):
        client, form, token = self._client_and_form(self.reader)
        self.assertEqual(
            form['action'], reverse('main:toggle_project_star', args=[self.project.pk]),
        )
        response = client.post(form['action'], HTTP_X_CSRFTOKEN=token)
        self.assertRedirects(
            response, self.project.get_absolute_url(), fetch_redirect_response=False,
        )
        self.assertTrue(self.project.starred_by.filter(pk=self.reader.pk).exists())

    def test_missing_csrf_and_expired_session_do_not_change_star(self):
        client, form, token = self._client_and_form(self.reader)
        self.project.starred_by.add(self.reader)

        missing_csrf = client.post(form['data-api-url'])
        self.assertEqual(missing_csrf.status_code, 403)
        self.assertTrue(self.project.starred_by.filter(pk=self.reader.pk).exists())

        client.logout()
        expired = client.post(form['data-api-url'], HTTP_X_CSRFTOKEN=token)
        self.assertEqual(expired.status_code, 403)
        self.assertEqual(list(self.project.starred_by.all()), [self.reader])

    def test_guest_sees_login_link_without_a_star_form(self):
        response = self.client.get(self.project.get_absolute_url())
        self.assertContains(response, 'Log in to star')
        parser = _ProjectStarFormParser()
        parser.feed(response.content.decode())
        self.assertEqual(parser.forms, [])
