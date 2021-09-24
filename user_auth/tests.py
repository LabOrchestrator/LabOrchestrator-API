import re

from ai_django_core.mail.services.tests import EmailTestService
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.urls import reverse
from commons.utils_testing import TokenLoginAPITestCase
from user.models import User

"""
EMAIL TESTING BLOG:
https://medium.com/ambient-innovation/thorough-and-reliable-unit-testing-of-emails-in-django-5f34901b1b16
"""


def user_json(user):
    return {"pk": user.id, "first_name": user.first_name, "last_name": user.last_name,
            "display_name": user.display_name, "real_display_name": user.get_real_display_name(),
            "email": user.email}


class EmailTestCase(TokenLoginAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email_test_service = EmailTestService()


class RegistrationAPIViewTestCase(EmailTestCase):
    url = reverse("rest_register")

    def user_json(self, user=None):
        if user is None:
            user = self.user
        return user_json(user)

    def test_registration(self):
        user_old_len = len(get_user_model().objects.all())
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                               "password2": "Geheim1234!", "first_name": "felix",
                                               "last_name": "blume", "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("key", response.data.keys())
        user_new_len = len(get_user_model().objects.all())
        # assert one user is registered
        self.assertEqual(user_old_len + 1, user_new_len)
        user = get_user_model().objects.filter(email="register@example.com").first()
        self.assertEqual(user.email, "register@example.com")
        # assert one email is send
        mails = self.email_test_service.all()
        mails.assert_quantity(1)
        # assert email contains text
        first_mail = mails.first()
        self.assertIn("confirm this is correct", first_mail.body)
        self.assertIn(reverse("account_email_verification_sent"), first_mail.body)
        self.assertIn("has given your e-mail address to register an account on", first_mail.body)

    def test_registration_email_constraint(self):
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                               "password2": "Geheim1234!", "first_name": "felix", "last_name": "blume",
                                               "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 201)
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                               "password2": "Geheim1234!", "first_name": "felix", "last_name": "blume",
                                               "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 400)
        errors = ["A user is already registered with this e-mail address."]
        self.assertDictEqual({"email": errors}, response.data)

    def test_registration_second_password_wrong(self):
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                               "password2": "Geheim4321!", "first_name": "felix", "last_name": "blume",
                                               "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 400)
        errors = ["The two password fields didn't match."]
        self.assertDictEqual({"non_field_errors": errors}, response.data)

    def test_registration_password_to_low(self):
        user_old_len = len(get_user_model().objects.all())
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "geheim",
                                               "password2": "geheim", "first_name": "felix", "last_name": "blume",
                                               "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 400)
        errors = ["This password is too short. It must contain at least 8 characters.", "This password is too common."]
        self.assertDictEqual({"password1": errors}, response.data)

    def test_registration_forgot_password2(self):
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                               "first_name": "felix", "last_name": "blume",
                                               "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 400)
        errors = ["This field is required."]
        self.assertDictEqual({"password2": errors}, response.data)

    def test_registration_invalid_mail(self):
        response = self.client.post(self.url, {"email": "invalid", "password1": "Geheim1234!",
                                               "password2": "Geheim1234!", "first_name": "felix", "last_name": "blume",
                                               "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 400)
        errors = ["Enter a valid email address."]
        self.assertDictEqual({"email": errors}, response.data)

    def test_registration_without_firstname(self):
        """Firstname shouldn't be empty."""
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                               "password2": "Geheim1234!", "last_name": "blume",
                                               "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 400)
        errors = ["This field is required."]
        self.assertDictEqual({"first_name": errors}, response.data)

    def test_registration_without_lastname(self):
        """Lastname should be empty."""
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                               "password2": "Geheim1234!", "first_name": "felix", "last_name": "",
                                               "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 201)

    def test_registration_without_displayname(self):
        """Displayname should be empty."""
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                               "password2": "Geheim1234!", "first_name": "felix", "last_name": "",
                                               "display_name": ""})
        self.assertEqual(response.status_code, 201)

    def test_registration_with_is_trusted(self):
        """Is trusted should not be true."""
        response = self.client.post(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                               "password2": "Geheim1234!", "first_name": "felix", "last_name": "",
                                               "display_name": "hallo", "is_trusted": "True"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.get(email="register@example.com").is_trusted)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_put(self):
        response = self.client.put(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                              "first_name": "felix", "last_name": "blume",
                                              "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 405)

    def test_patch(self):
        response = self.client.patch(self.url, {"email": "register@example.com"})
        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)


class RegistrationVerificationAPIViewTestCase(EmailTestCase):
    url = reverse("account_email_verification_sent")

    def test_registration_verify(self):
        user_creation_json = {"email": "register@example.com", "password1": "Geheim1234!", "password2": "Geheim1234!",
                              "first_name": "felix", "last_name": "blume",
                              "display_name": "Günther Baum"}
        response = self.client.post(reverse("rest_register"), user_creation_json)
        # creation works
        self.assertEqual(response.status_code, 201)
        # get user
        user = get_user_model().objects.filter(email="register@example.com").first()
        # get email object
        email = EmailAddress.objects.filter(user=user).first()
        # email shouldn't be verified
        self.assertFalse(email.verified)
        # get key from mail
        mails = self.email_test_service.all()
        first_mail = mails.first()
        url = "http://(.*)/rest-auth/registration/verify-email/([-:\w]+)/"
        regex = f"To confirm this is correct, go to {url}\n\nThank you for using"
        match = re.search(regex, first_mail.body)
        self.assertEqual(len(match.groups()), 2)
        key = match.group(2)
        # verify user
        response = self.client.post(self.url, {"key": key})
        # verification works
        self.assertEqual(response.status_code, 200)
        # email is verified
        email = EmailAddress.objects.filter(user=user).first()
        self.assertTrue(email.verified)

    def test_registration_verify_wrong_key(self):
        user_creation_json = {"email": "register@example.com", "password1": "Geheim1234!", "password2": "Geheim1234!",
                              "first_name": "felix", "last_name": "blume",
                              "display_name": "Günther Baum"}
        response = self.client.post(reverse("rest_register"), user_creation_json)
        # creation works
        self.assertEqual(response.status_code, 201)
        # get user
        user = get_user_model().objects.filter(email="register@example.com").first()
        # get email object
        email = EmailAddress.objects.filter(user=user).first()
        # email shouldn't be verified
        self.assertFalse(email.verified)
        key = "wrongkey"
        # verify user
        response = self.client.post(self.url, {"key": key})
        # verification doesn't work
        self.assertEqual(response.status_code, 404)
        # email is not verified
        email = EmailAddress.objects.filter(user=user).first()
        self.assertFalse(email.verified)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_put(self):
        response = self.client.put(self.url, {"email": "register@example.com", "password1": "Geheim1234!",
                                              "first_name": "felix", "last_name": "blume",
                                              "display_name": "Günther Baum"})
        self.assertEqual(response.status_code, 405)

    def test_patch(self):
        response = self.client.patch(self.url, {"email": "register@example.com"})
        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)


class MeAPIViewTestCase(EmailTestCase):
    url = reverse("rest_user_details")

    def get_me_json(self, user):
        return {"pk": user.id, "email": user.email, "first_name": user.first_name,
                "last_name": user.last_name, "display_name": user.display_name,
                "real_display_name": user.get_real_display_name()}

    def test_get(self):
        me_json = self.get_me_json(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, me_json)

    def test_get_without_authorization(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_put(self):
        me_json = self.get_me_json(self.user)
        self.assertNotEqual(me_json["first_name"], "Bernd")
        self.assertNotEqual(me_json["last_name"], "Brot")
        self.assertNotEqual(me_json["email"], "felix@blume.de")
        self.assertNotEqual(me_json["display_name"], "Felix Blume")
        self.assertNotEqual(me_json["pk"], 202)
        data = {"first_name": "Bernd", "last_name": "Brot", "email": "felix@blume.de",
                "display_name": "Felix Blume", "pk": 202}
        response = self.client.put(self.url, data)
        me_json["first_name"] = "Bernd"
        me_json["last_name"] = "Brot"
        me_json["display_name"] = "Felix Blume"
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, me_json)
        self.assertNotEqual(me_json["email"], "felix@blume.de")
        self.assertNotEqual(me_json["pk"], 202)

    def test_put_without_authorization(self):
        self.client.logout()
        data = {"first_name": "Felix", "last_name": "Blume", "email": "felix@blume.de", "display_name": "Felix Blume",
                "pk": 202}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 401)

    def test_patch_first_name(self):
        me_json = self.get_me_json(self.user)
        self.assertNotEqual(me_json["first_name"], "Bernd")
        response = self.client.patch(self.url, {"first_name": "Bernd"})
        me_json["first_name"] = "Bernd"
        me_json["real_display_name"] = "Bernd Blume"
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, me_json)

    def test_patch_no_empty_first_name(self):
        """Test if firstname can't be patched to empty name."""
        me_json = self.get_me_json(self.user)
        response = self.client.patch(self.url, {"first_name": ""})
        self.assertEqual(response.status_code, 400)

    def test_patch_no_empty_is_trusted(self):
        """Test if firstname can't be patched to empty name."""
        me_json = self.get_me_json(self.user)
        response = self.client.patch(self.url, {"is_trusted": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.is_trusted)

    def test_patch_last_name(self):
        me_json = self.get_me_json(self.user)
        self.assertNotEqual(me_json["last_name"], "Brot")
        response = self.client.patch(self.url, {"last_name": "Brot"})
        me_json["last_name"] = "Brot"
        me_json["real_display_name"] = "Felix Brot"
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, me_json)

    def test_patch_empty_last_name(self):
        """Test if lastname can be patched to empty name."""
        me_json = self.get_me_json(self.user)
        self.assertNotEqual(me_json["last_name"], "")
        response = self.client.patch(self.url, {"last_name": ""})
        me_json["last_name"] = ""
        me_json["real_display_name"] = "Felix"
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, me_json)

    def test_patch_display_name(self):
        me_json = self.get_me_json(self.user)
        self.assertNotEqual(me_json["display_name"], "Felix Blume")
        response = self.client.patch(self.url, {"display_name": "Felix Blume"})
        me_json["display_name"] = "Felix Blume"
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, me_json)

    def test_patch_empty_display_name(self):
        me_json = self.get_me_json(self.user)
        response = self.client.patch(self.url, {"display_name": ""})
        me_json["display_name"] = ""
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, me_json)

    def test_patch_not_email(self):
        me_json = self.get_me_json(self.user)
        self.assertNotEqual(me_json["email"], "felix@blume.de")
        response = self.client.patch(self.url, {"email": "felix@blume.de"})
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(me_json["email"], "felix@blume.de")

    def test_patch_not_pk(self):
        me_json = self.get_me_json(self.user)
        self.assertNotEqual(me_json["pk"], 202)
        response = self.client.patch(self.url, {"pk": 202})
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(me_json["pk"], 202)

    def test_patch_without_authorization(self):
        self.client.logout()
        data = {"first_name": "Felix", "last_name": "Blume", "email": "felix@blume.de", "display_name": "Felix Blume",
                "pk": 202}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 401)

    def test_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_without_auth(self):
        self.client.logout()
        data = {"first_name": "Felix", "last_name": "Blume", "email": "felix@blume.de", "display_name": "Felix Blume"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_delete_without_auth(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)


class LoginAPIViewTestCase(EmailTestCase):
    url = reverse("rest_login")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_get_without_authorization(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_put(self):
        data = {"email": "newuser@example.com", "password": "Geheim1234!"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_put_without_authorization(self):
        self.client.logout()
        data = {"email": "newuser@example.com", "password": "Geheim1234!"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_patch(self):
        data = {"email": "newuser@example.com", "password": "Geheim1234!"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_patch_without_authorization(self):
        self.client.logout()
        data = {"email": "newuser@example.com", "password": "Geheim1234!"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_delete_without_authorization(self):
        self.client.logout()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post(self):
        user = self.user
        user_data = {"pk": user.id, "email": user.email, "first_name": user.first_name,
                     "last_name": user.last_name, "display_name": user.display_name,
                     "real_display_name": user.get_real_display_name()}
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)
        self.client.logout()
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 401)
        data = {"email": "user@domain.com", "password": "geheim"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("key", response.data.keys())
        key = response.data["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)

    def test_post_wrong_pw(self):
        user = self.user
        user_data = {"pk": user.id, "email": user.email, "first_name": user.first_name,
                     "last_name": user.last_name, "display_name": user.display_name,
                     "real_display_name": user.get_real_display_name()}
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)
        self.client.logout()
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 401)
        data = {"email": "user@domain.com", "password": "falsch"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, {"non_field_errors": ["Unable to log in with provided credentials."]})

    def test_post_wrong_email(self):
        user = self.user
        user_data = {"pk": user.id, "email": user.email, "first_name": user.first_name,
                     "last_name": user.last_name, "display_name": user.display_name,
                     "real_display_name": user.get_real_display_name()}
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)
        self.client.logout()
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 401)
        data = {"email": "falschemail@domain.com", "password": "geheim"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, {"non_field_errors": ["Unable to log in with provided credentials."]})


class LogoutAPIViewTestCase(EmailTestCase):
    url = reverse("rest_logout")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_get_without_authorization(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_put(self):
        data = {"email": "newuser@example.com", "password": "Geheim1234!"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_put_without_authorization(self):
        self.client.logout()
        data = {"email": "newuser@example.com", "password": "Geheim1234!"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_patch(self):
        data = {"email": "newuser@example.com", "password": "Geheim1234!"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_patch_without_authorization(self):
        self.client.logout()
        data = {"email": "newuser@example.com", "password": "Geheim1234!"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_delete_without_authorization(self):
        self.client.logout()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post(self):
        user = self.user
        user_data = {"pk": user.id, "email": user.email, "first_name": user.first_name,
                     "last_name": user.last_name, "display_name": user.display_name,
                     "real_display_name": user.get_real_display_name()}
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)
        self.client.logout()
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 401)
        data = {"email": "user@domain.com", "password": "geheim"}
        response = self.client.post(reverse("rest_login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("key", response.data.keys())
        key = response.data["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)
        logout_response = self.client.post(self.url)
        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(logout_response.data, {"detail": "Successfully logged out."})
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 401)


class PasswordChangeAPIViewTestCase(EmailTestCase):
    url = reverse("rest_password_change")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_get_without_authorization(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_put(self):
        data = {"password1": "Geheim1234!", "password2": "Geheim1234!"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_put_without_authorization(self):
        self.client.logout()
        data = {"password1": "Geheim1234!", "password2": "Geheim1234!"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 401)

    def test_patch(self):
        data = {"password1": "Geheim1234!", "password2": "Geheim1234!"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_patch_without_authorization(self):
        self.client.logout()
        data = {"password1": "Geheim1234!", "password2": "Geheim1234!"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 401)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_delete_without_authorization(self):
        self.client.logout()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)

    def test_post(self):
        # assert logging in works
        self.client.logout()
        user = self.user
        user_data = {"pk": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
                     "display_name": user.display_name, "real_display_name": user.get_real_display_name()}
        data = {"email": "user@domain.com", "password": "geheim"}
        response = self.client.post(reverse("rest_login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("key", response.data.keys())
        key = response.data["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)
        # change password
        change_data = {"new_password1": "Geheim1234!", "new_password2": "Geheim1234!"}
        change_response = self.client.post(self.url, change_data)
        self.assertEqual(change_response.status_code, 200)
        self.assertDictEqual(change_response.data, {"detail": "New password has been saved."})
        # assert logging in works with new password
        self.client.logout()
        data = {"email": "user@domain.com", "password": "Geheim1234!"}
        response = self.client.post(reverse("rest_login"), data)
        self.assertIn("key", response.data.keys())
        key = response.data["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)

    def test_post_wrong_password(self):
        # assert logging in works
        self.client.logout()
        user = self.user
        user_data = {"pk": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
                     "display_name": user.display_name, "real_display_name": user.get_real_display_name()}
        data = {"email": "user@domain.com", "password": "geheim"}
        response = self.client.post(reverse("rest_login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("key", response.data.keys())
        key = response.data["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)
        # change password
        change_data = {"new_password1": "geheim1", "new_password2": "Geheim1234!"}
        change_response = self.client.post(self.url, change_data)
        self.assertEqual(change_response.status_code, 400)
        self.assertDictEqual(change_response.data, {"new_password2": ["The two password fields didn’t match."]})

    def test_post_password_not_strong(self):
        # assert logging in works
        self.client.logout()
        user = self.user
        user_data = {"pk": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
                     "display_name": user.display_name, "real_display_name": user.get_real_display_name()}
        data = {"email": "user@domain.com", "password": "geheim"}
        response = self.client.post(reverse("rest_login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("key", response.data.keys())
        key = response.data["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)
        # change password
        change_data = {"new_password1": "geheim1", "new_password2": "geheim1"}
        change_response = self.client.post(self.url, change_data)
        self.assertEqual(change_response.status_code, 400)
        errors = ["This password is too short. It must contain at least 8 characters."]
        self.assertDictEqual(change_response.data, {"new_password2": errors})

    def test_post_without_authorization(self):
        # assert logging in works
        self.client.logout()
        user = self.user
        user_data = {"pk": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
                     "display_name": user.display_name, "real_display_name": user.get_real_display_name()}
        data = {"email": "user@domain.com", "password": "geheim"}
        response = self.client.post(reverse("rest_login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("key", response.data.keys())
        key = response.data["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)
        # change password
        self.client.logout()
        change_data = {"new_password1": "Geheim1234!", "new_password2": "Geheim1234!"}
        change_response = self.client.post(self.url, change_data)
        self.assertEqual(change_response.status_code, 401)


class PasswordResetAPIViewTestCase(EmailTestCase):
    url = reverse("rest_password_reset")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_get_without_authorization(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_put(self):
        data = {"password1": "Geheim1234!", "password2": "Geheim1234!"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_put_without_authorization(self):
        self.client.logout()
        data = {"password1": "Geheim1234!", "password2": "Geheim1234!"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_patch(self):
        data = {"password1": "Geheim1234!", "password2": "Geheim1234!"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_patch_without_authorization(self):
        self.client.logout()
        data = {"password1": "Geheim1234!", "password2": "Geheim1234!"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_delete_without_authorization(self):
        self.client.logout()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post(self):
        response = self.client.post(self.url, {"email": self.user.email})
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, {"detail": "Password reset e-mail has been sent."})
        mails = self.email_test_service.all()
        mails.assert_quantity(1)
        # assert email contains text
        first_mail = mails.first()
        self.assertIn("requested a password", first_mail.body)
        self.assertIn(reverse("rest_password_reset_confirm"), first_mail.body)

    def test_post_wrong_email(self):
        response = self.client.post(self.url, {"email": "wrongemail"})
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, {"email": ["Enter a valid email address."]})


class PasswordResetConfirmAPIViewTestCase(EmailTestCase):
    url = reverse("rest_password_reset_confirm")

    def get_data(self, uid, token, password1="Geheim1234!", password2="Geheim1234!"):
        return {"new_password1": password1, "new_password2": password2, "uid": uid, "token": token}

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_get_without_authorization(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_put(self):
        data = self.get_data("id", "token")
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_put_without_authorization(self):
        self.client.logout()
        data = self.get_data("id", "token")
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_patch(self):
        data = self.get_data("id", "token")
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_patch_without_authorization(self):
        self.client.logout()
        data = self.get_data("id", "token")
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_delete_without_authorization(self):
        self.client.logout()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post(self):
        # assert logging in works
        self.client.logout()
        user = self.user
        user_data = {"pk": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
                     "display_name": user.display_name}
        data = {"email": "user@domain.com", "password": "geheim"}
        response = self.client.post(reverse("rest_login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("key", response.data.keys())
        key = response.data["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        user_data["real_display_name"] = user.get_real_display_name()
        self.assertDictEqual(user_response.data, user_data)
        # request password reset
        response = self.client.post(reverse("rest_password_reset"), {"email": self.user.email})
        # assert password reset was generated correctly
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, {"detail": "Password reset e-mail has been sent."})
        mails = self.email_test_service.all()
        mails.assert_quantity(1)
        # assert email contains text
        first_mail = mails.first()
        self.assertIn("requested a password", first_mail.body)
        self.assertIn(reverse("rest_password_reset_confirm"), first_mail.body)
        # get uid and token from email
        uid_pattern = ".*password/reset/confirm/(.*?)/(.*?)/"
        uid_match = re.search(uid_pattern, first_mail.body)
        self.assertEqual(len(uid_match.groups()), 2)
        uid = uid_match.group(1)
        token = uid_match.group(2)
        password = "Geheim1234!"
        reset_data = self.get_data(uid, token, password1=password, password2=password)
        # change password
        reset_response = self.client.post(self.url, reset_data)
        self.assertEqual(reset_response.status_code, 200)
        self.assertDictEqual(reset_response.data, {"detail": "Password has been reset with the new password."})
        # assert logging in works with new password
        self.client.logout()
        data = {"email": "user@domain.com", "password": "Geheim1234!"}
        response = self.client.post(reverse("rest_login"), data)
        self.assertIn("key", response.data.keys())
        key = response.data["key"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        user_response = self.client.get(reverse("rest_user_details"), user_data)
        self.assertEqual(user_response.status_code, 200)
        self.assertDictEqual(user_response.data, user_data)

    def test_post_wrong_key(self):
        # request password reset
        response = self.client.post(reverse("rest_password_reset"), {"email": self.user.email})
        # assert password reset was generated correctly
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, {"detail": "Password reset e-mail has been sent."})
        mails = self.email_test_service.all()
        mails.assert_quantity(1)
        # assert email contains text
        first_mail = mails.first()
        self.assertIn("requested a password", first_mail.body)
        self.assertIn(reverse("rest_password_reset_confirm"), first_mail.body)
        # get uid and token from email
        uid_pattern = ".*password/reset/confirm/(.*?)/(.*?)/"
        uid_match = re.search(uid_pattern, first_mail.body)
        self.assertEqual(len(uid_match.groups()), 2)
        uid = uid_match.group(1)
        token = uid_match.group(2)
        password = "Geheim1234!"
        reset_data = self.get_data(uid, token, password1="Geheim4321!", password2=password)
        # change password
        reset_response = self.client.post(self.url, reset_data)
        self.assertEqual(reset_response.status_code, 400)
        self.assertEqual(reset_response.data, {"new_password2": ["The two password fields didn’t match."]})

    def test_post_password_to_low(self):
        # request password reset
        response = self.client.post(reverse("rest_password_reset"), {"email": self.user.email})
        # assert password reset was generated correctly
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, {"detail": "Password reset e-mail has been sent."})
        mails = self.email_test_service.all()
        mails.assert_quantity(1)
        # assert email contains text
        first_mail = mails.first()
        self.assertIn("requested a password", first_mail.body)
        self.assertIn(reverse("rest_password_reset_confirm"), first_mail.body)
        # get uid and token from email
        uid_pattern = ".*password/reset/confirm/(.*?)/(.*?)/"
        uid_match = re.search(uid_pattern, first_mail.body)
        self.assertEqual(len(uid_match.groups()), 2)
        uid = uid_match.group(1)
        token = uid_match.group(2)
        password = "geheim"
        reset_data = self.get_data(uid, token, password1=password, password2=password)
        # change password
        reset_response = self.client.post(self.url, reset_data)
        self.assertEqual(reset_response.status_code, 400)
        self.assertEqual(reset_response.data, {"new_password2": ["This password is too short. It must contain at least 8 characters.", "This password is too common."]})

    def test_post_invalid_token(self):
        # request password reset
        response = self.client.post(reverse("rest_password_reset"), {"email": self.user.email})
        # assert password reset was generated correctly
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, {"detail": "Password reset e-mail has been sent."})
        mails = self.email_test_service.all()
        mails.assert_quantity(1)
        # assert email contains text
        first_mail = mails.first()
        self.assertIn("requested a password", first_mail.body)
        self.assertIn(reverse("rest_password_reset_confirm"), first_mail.body)
        # get uid and token from email
        uid_pattern = ".*password/reset/confirm/(.*?)/(.*?)/"
        uid_match = re.search(uid_pattern, first_mail.body)
        self.assertEqual(len(uid_match.groups()), 2)
        uid = uid_match.group(1)
        token = "falsch"
        password = "geheim"
        reset_data = self.get_data(uid, token, password1=password, password2=password)
        # change password
        reset_response = self.client.post(self.url, reset_data)
        self.assertEqual(reset_response.status_code, 400)
        self.assertEqual(reset_response.data, {"token": ["Invalid value"]})

    def test_post_invalid_uid(self):
        # request password reset
        response = self.client.post(reverse("rest_password_reset"), {"email": self.user.email})
        # assert password reset was generated correctly
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, {"detail": "Password reset e-mail has been sent."})
        mails = self.email_test_service.all()
        mails.assert_quantity(1)
        # assert email contains text
        first_mail = mails.first()
        self.assertIn("requested a password", first_mail.body)
        self.assertIn(reverse("rest_password_reset_confirm"), first_mail.body)
        # get uid and token from email
        uid_pattern = ".*password/reset/confirm/(.*?)/(.*?)/"
        uid_match = re.search(uid_pattern, first_mail.body)
        self.assertEqual(len(uid_match.groups()), 2)
        token = uid_match.group(2)
        uid = "falsch"
        password = "geheim"
        reset_data = self.get_data(uid, token, password1=password, password2=password)
        # change password
        reset_response = self.client.post(self.url, reset_data)
        self.assertEqual(reset_response.status_code, 400)
        self.assertEqual(reset_response.data, {"uid": ["Invalid value"]})
