from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class ModelAPITestCase(APITestCase):
    model = None

    def assertDeleted(self, response, id):
        if self.model is None:
            raise Exception("model not set")
        self.assertEqual(204, response.status_code)
        self.assertFalse(self.model.objects.filter(pk=id).exists())


class TokenLoginAPITestCase(APITestCase):
    """Provides methods to login with new created users and authenticates them with a token."""

    def login(self, user=None):
        if user is None:
            user = self.user
        self.token = Token.objects.create(user=user)
        self.api_authentication()

    def create_user(self, email, password, first_name="Felix", last_name="Blume", **kwargs):
        return get_user_model().objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, **kwargs)

    def create_user_and_login(self, email, password, first_name="Felix", last_name="Blume", **kwargs):
        user = self.create_user(email, password, first_name, last_name, **kwargs)
        self.email = email
        self.password = password
        self.user = user
        self.login(self.user)

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def login_as_default_user(self):
        """Create a default user and login with it"""
        self.create_user_and_login("user@domain.com", "geheim")

    def login_as_default_user_2(self):
        """Create another default user and login with it"""
        self.create_user_and_login("user2@domain.com", "geheim")

    def login_as_admin(self):
        """Create an admin user and login with it"""
        self.create_user_and_login("admin@domain.com", "geheimer", is_staff=True)

    def setUp(self):
        """Create a default user and login with it"""
        self.login_as_default_user()
