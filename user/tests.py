from django.urls import reverse
from rest_framework import serializers

from commons.utils_testing import TokenLoginAPITestCase


def user_json(user):
    return {"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "email": user.email,
            "full_name": user.get_full_name(), "display_name": user.display_name,
            "real_display_name": user.get_real_display_name(),
            "date_joined": serializers.DateTimeField().to_representation(user.date_joined),
            "is_active": user.is_active, "is_staff": user.is_staff, "is_superuser": user.is_superuser,
            }


class UserListAPIViewTestCase(TokenLoginAPITestCase):
    url = reverse("user:user-list")

    def user_json(self, user=None):
        if user is None:
            user = self.user
        return user_json(user)

    def test_get_my_user_without_admin(self):
        """You should see only your user and not others."""
        self.login_as_default_user_2()
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], self.user_json())

    def test_get_my_user_with_admin(self):
        """You should see all users."""
        old_user = self.user
        self.login_as_admin()
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 2)
        users_json = [self.user_json(old_user), self.user_json(self.user)]
        self.assertListEqual(response.data, users_json)

    def test_get_without_authorization(self):
        """You should get an error."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)


class UserDetailAPIViewTestCase(TokenLoginAPITestCase):

    def url(self, pk):
        return reverse("user:user-detail", args=[pk])

    def user_json(self, user=None):
        if user is None:
            user = self.user
        return user_json(user)

    def test_get_my_user_without_admin(self):
        """You should see only your user and not others."""
        self.login_as_default_user_2()
        response = self.client.get(self.url(self.user.id))
        self.assertEqual(response.data, self.user_json())

    def test_get_other_user_without_admin(self):
        """You should not see other users."""
        old_user = self.user
        self.login_as_default_user_2()
        response = self.client.get(self.url(old_user.id))
        self.assertEqual(response.status_code, 404)

    def test_get_my_user_with_admin(self):
        """You should see all users."""
        old_user = self.user
        self.login_as_admin()
        response = self.client.get(self.url(self.user.id))
        self.assertEqual(response.data, self.user_json(self.user))
        response = self.client.get(self.url(old_user.id))
        self.assertEqual(response.data, self.user_json(old_user))

    def test_get_without_authorization(self):
        """You should get an error."""
        self.client.logout()
        response = self.client.get(self.url(self.user.id))
        self.assertEqual(response.status_code, 401)


class UserOtherMethodsAPIViewTestCase(TokenLoginAPITestCase):

    def url(self, pk):
        return reverse("user:user-detail", args=[pk])

    def test_create_new_user_logged_in(self):
        response = self.client.post(self.url(self.user.id), {"email": "neue@mail.de", "password": "geheim"})
        self.assertEqual(response.status_code, 405)

    def test_create_new_user_with_admin(self):
        self.login_as_admin()
        response = self.client.post(self.url(self.user.id), {"email": "neue@mail.de", "password": "geheim"})
        self.assertEqual(response.status_code, 405)

    def test_create_new_user_without_login(self):
        self.client.logout()
        response = self.client.post(self.url(self.user.id), {"email": "neue@mail.de", "password": "geheim"})
        self.assertEqual(response.status_code, 401)

    def test_put_logged_in(self):
        response = self.client.put(self.url(self.user.id), {"email": "neue@mail.de", "password": "geheim"})
        self.assertEqual(response.status_code, 405)

    def test_put_with_admin(self):
        self.login_as_admin()
        response = self.client.put(self.url(self.user.id), {"email": "neue@mail.de", "password": "geheim"})
        self.assertEqual(response.status_code, 405)

    def test_put_without_login(self):
        self.client.logout()
        response = self.client.put(self.url(self.user.id), {"email": "neue@mail.de", "password": "geheim"})
        self.assertEqual(response.status_code, 401)

    def test_patch_logged_in(self):
        response = self.client.patch(self.url(self.user.id), {"email": "neue@mail.de"})
        self.assertEqual(response.status_code, 405)

    def test_patch_with_admin(self):
        self.login_as_admin()
        response = self.client.patch(self.url(self.user.id), {"email": "neue@mail.de"})
        self.assertEqual(response.status_code, 405)

    def test_patch_without_login(self):
        self.client.logout()
        response = self.client.patch(self.url(self.user.id), {"email": "neue@mail.de"})
        self.assertEqual(response.status_code, 401)

    def test_patch_password_logged_in(self):
        response = self.client.patch(self.url(self.user.id), {"password": "geheim"})
        self.assertEqual(response.status_code, 405)

    def test_patch_password_with_admin(self):
        self.login_as_admin()
        response = self.client.patch(self.url(self.user.id), {"password": "geheim"})
        self.assertEqual(response.status_code, 405)

    def test_patch_password_new_user_without_login(self):
        self.client.logout()
        response = self.client.patch(self.url(self.user.id), {"password": "geheim"})
        self.assertEqual(response.status_code, 401)

    def test_delete_logged_in(self):
        response = self.client.delete(self.url(self.user.id))
        self.assertEqual(response.status_code, 405)

    def test_delete_with_admin(self):
        self.login_as_admin()
        response = self.client.delete(self.url(self.user.id))
        self.assertEqual(response.status_code, 405)

    def test_delete_without_login(self):
        self.client.logout()
        response = self.client.delete(self.url(self.user.id))
        self.assertEqual(response.status_code, 401)
