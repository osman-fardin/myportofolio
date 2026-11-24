from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from .models import Experience


class TokenIntegrationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser('token-owner', password='Test-only-8492!')
        cls.reader = get_user_model().objects.create_user('token-reader', password='Test-only-8492!')
        cls.editor = get_user_model().objects.create_user('token-editor', password='Test-only-8492!')
        cls.editor.user_permissions.add(Permission.objects.get(codename='change_experience'))

    def authenticate_token(self, user):
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return token

    def test_login_and_invalid_credentials(self):
        response = self.client.post('/api/v1/auth/token/', {'username': 'token-owner', 'password': 'Test-only-8492!'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['token'], Token.objects.get(user=self.owner).key)
        self.assertEqual(self.client.post('/api/v1/auth/token/', {'username': 'token-owner', 'password': 'wrong'}).status_code, 400)

    def test_public_projects_remain_accessible(self):
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_owner_can_create_project_with_token_without_csrf(self):
        self.authenticate_token(self.owner)
        response = self.client.post('/api/v1/projects/', {
            'title': 'Token project', 'project_type': 'Web', 'role': 'Developer',
            'description': 'Created in isolated test database.', 'technologies': 'Flutter\nDjango',
            'live_url': 'https://example.com/',
        }, format='json')
        self.assertEqual(response.status_code, 201)

    def test_reader_and_editor_cannot_create_projects(self):
        for user in (self.reader, self.editor):
            self.authenticate_token(user)
            self.assertEqual(self.client.post('/api/v1/projects/', {}, format='json').status_code, 403)

    def test_experience_four_roles_keep_their_permissions_with_tokens(self):
        experience = Experience.objects.create(title='Role regression', description='Token role test')
        url = f'/api/v1/experiences/{experience.pk}/'
        self.authenticate_token(self.editor)
        self.assertEqual(self.client.patch(url, {'title': 'Edited'}, format='json').status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 403)
        self.authenticate_token(self.reader)
        self.assertEqual(self.client.patch(url, {'title': 'Blocked'}, format='json').status_code, 403)
        self.client.credentials()
        self.assertEqual(self.client.patch(url, {'title': 'Guest'}, format='json').status_code, 403)
        self.authenticate_token(self.owner)
        self.assertEqual(self.client.delete(url).status_code, 204)

    def test_logout_revokes_only_callers_token_and_reuse_returns_401(self):
        token = self.authenticate_token(self.owner)
        other = Token.objects.create(user=self.reader)
        self.assertEqual(self.client.post('/api/v1/auth/logout/').status_code, 204)
        self.assertFalse(Token.objects.filter(pk=token.pk).exists())
        self.assertTrue(Token.objects.filter(pk=other.pk).exists())
        self.assertEqual(self.client.get('/api/v1/projects/').status_code, 401)

    def test_logout_requires_authentication(self):
        self.assertEqual(self.client.post('/api/v1/auth/logout/').status_code, 401)

    def test_invalid_token_does_not_fall_back_to_browser_session(self):
        self.client.force_login(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid')
        self.assertEqual(self.client.get('/api/v1/projects/').status_code, 401)

    def test_session_logout_does_not_revoke_an_unrelated_token(self):
        token = Token.objects.create(user=self.owner)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post('/api/v1/auth/logout/').status_code, 204)
        self.assertTrue(Token.objects.filter(pk=token.pk).exists())

    def test_session_writes_still_require_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post('/api/v1/projects/', {}, format='json').status_code, 403)

    def test_cors_allows_local_web_origin_and_authorization_preflight(self):
        response = self.client.options('/api/v1/projects/', HTTP_ORIGIN='http://localhost:8774',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST', HTTP_ACCESS_CONTROL_REQUEST_HEADERS='authorization,content-type')
        self.assertEqual(response['Access-Control-Allow-Origin'], 'http://localhost:8774')
        self.assertIn('authorization', response['Access-Control-Allow-Headers'])
        response = self.client.get('/api/v1/projects/', HTTP_ORIGIN='https://untrusted.example')
        self.assertNotIn('Access-Control-Allow-Origin', response)

    def test_inactive_user_cannot_obtain_or_use_token(self):
        self.reader.is_active = False
        self.reader.save()
        self.authenticate_token(self.reader)
        self.assertEqual(self.client.get('/api/v1/projects/').status_code, 401)
        self.client.credentials()
        self.assertEqual(self.client.post('/api/v1/auth/token/', {'username':'token-reader','password':'Test-only-8492!'}).status_code, 400)
