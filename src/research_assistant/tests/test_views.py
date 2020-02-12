from django.contrib.auth import get_user
from django.test import tag
from django.urls import reverse
from encryption_compendium.test_utils import (
    random_email,
    random_username,
    random_password,
    UnitTest,
)
from research_assistant.models import CompendiumEntryTag, EmailVerificationToken, User
from unittest import skip

"""
---------------------------------------------------
Tests for the login view
---------------------------------------------------
"""


@tag("auth", "login")
class LoginTestCase(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)
        self.login_data = {"username": self.username, "password": self.password}

    def test_login_as_existing_user(self):
        response = self.client.get(reverse("research login"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "login.html")

        self.client.post(reverse("research login"), self.login_data)
        self.assertTrue(get_user(self.client).is_authenticated)

    def test_invalid_login(self):
        ### Use a nonexistent username
        login_data = {"username": random_username(self.rd), "password": self.password}
        self.client.post(reverse("research login"), login_data)
        self.assertFalse(get_user(self.client).is_authenticated)

        ### Use an existing username, but an incorrect password
        original_db_entry = User.objects.get(username=self.username).password
        login_data = {"username": self.username, "password": random_password(self.rd)}
        self.client.post(reverse("research login"), login_data)
        self.assertFalse(get_user(self.client).is_authenticated)

        # Database should not have changed
        self.assertEqual(
            original_db_entry, User.objects.get(username=self.username).password
        )


"""
---------------------------------------------------
Tests for email verification and user signup
---------------------------------------------------
"""


@tag("auth")
class AddNewUserTest(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)
        self.user.is_staff = True
        self.user.save()
        self.new_user_email = random_email(self.rd)
        self.form_data = {"email": self.new_user_email}

    def test_page_uses_correct_templates(self):
        response = self.client.get(reverse("add new user"))
        self.assertTemplateUsed("base.html")
        self.assertTemplateUsed("dashboard_base.html")
        self.assertTemplateUsed("add_user.html")

    @tag("email")
    def test_add_new_user_to_site(self):
        # Have the staff user send a new email verification token to get
        # a new user signed up.
        self.assertEqual(len(EmailVerificationToken.objects.all()), 0)
        response = self.client.post(reverse("add new user"), self.form_data)

        self.assertEqual(len(EmailVerificationToken.objects.all()), 1)
        tokens = EmailVerificationToken.objects.all()

        self.assertTrue(
            EmailVerificationToken.objects.filter(email=self.new_user_email).exists()
        )

        # TODO: check that email was sent
        self.fail("TODO")

    def test_only_staff_users_can_add_new_users(self):
        # Only users that are staff members can send email verification tokens
        self.fail("TODO")


"""
---------------------------------------------------
Tests for user logout
---------------------------------------------------
"""


class LogoutTestCase(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)

    def test_logout(self):
        # Since we passed preauth=True in the UnitTest setUp function, we should
        # already be authenticated with the site.
        self.assertTrue(get_user(self.client).is_authenticated)

        # Simulate hitting the "logout" button
        self.client.get(reverse("research logout"))
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_no_redirect_login_to_logout(self):
        # Normally, if we try to visit a page in the researcher interface before
        # logging in, we should be redirected to that page after a successful
        # login. However, this should not apply if we try to go to the logout
        # endpoint.
        self.client.logout()
        self.assertFalse(get_user(self.client).is_authenticated)

        login_url = reverse("research login")
        response = self.client.get(reverse("research logout"), follow=True)
        location, _ = response.redirect_chain[-1]
        self.assertEqual(location, login_url)

        self.client.post(
            location, {"username": self.username, "password": self.password}
        )
        self.assertTrue(get_user(self.client).is_authenticated)


"""
---------------------------------------------------
Tests for dashboard view
---------------------------------------------------
"""


class DashboardTestCase(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)

    def test_visit_dashboard_as_authenticated_user(self):
        # When we're logged in, we should be able to visit the user dashboard
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("research dashboard"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "dashboard_base.html")
        self.assertTemplateUsed(response, "dashboard.html")

    def test_try_to_visit_dashboard_unauthenticated(self):
        login_url = reverse("research login")
        dashboard_url = reverse("research dashboard")

        # The dashboard should redirect us to the login page when we haven't logged
        # in yet.
        response = self.client.get(dashboard_url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Client should be redirected to /research/login?next=/research/dashboard,
        # so that it's redirected to the dashboard after login.
        location, _ = response.redirect_chain[-1]
        self.assertTrue(location.startswith(login_url))

        expected_url = f"{login_url}?next={dashboard_url}"


"""
---------------------------------------------------
Tests for view to add new tags
---------------------------------------------------
"""


@tag("compendium-entries")
class NewTagTestCase(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)
        self.new_tag_page = reverse("research add tag")

    def test_new_tag_page_layout(self):
        # Visit the page for adding new tags and ensure that it obeys the
        # correct layouts
        response = self.client.get(self.new_tag_page)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "dashboard_base.html")
        self.assertTemplateUsed(response, "new_tag.html")

    def test_add_tag_to_database(self):
        # By default there shouldn't be any tags in the database
        self.assertEqual(len(CompendiumEntryTag.objects.all()), 0)

        # Add a new tag to the database through the new tag page
        data = {"tagname": "my-test-tag-name"}
        response = self.client.post(self.new_tag_page, data)

        # New tag should now appear in the database
        tags = CompendiumEntryTag.objects.all()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].tagname, "my-test-tag-name")

    def test_get_error_if_tag_is_invalid(self):
        ### Try to add a new tag to the database twice
        data = {"tagname": "test-tag"}
        response = self.client.post(self.new_tag_page, data)
        self.assertTrue(CompendiumEntryTag.objects.filter(tagname="test-tag").exists())

        response = self.client.post(self.new_tag_page, data)
        self.assertEqual(len(CompendiumEntryTag.objects.all()), 1)
        self.assertIn(
            "Compendium entry tag with this Tagname already exists.",
            response.content.decode("utf-8"),
        )

        ### Try to add a blank tag to the database
        data["tagname"] = ""
        response = self.client.post(self.new_tag_page, data)
        self.assertEqual(len(CompendiumEntryTag.objects.all()), 1)
        self.assertIn("This field is required.", response.content.decode("utf-8"))

    @skip("TODO")
    def test_add_invalid_tag(self):
        # Try to add an invalid tag to the database
        self.fail("TODO")
