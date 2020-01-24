from django.contrib.auth import get_user
from django.test import tag
from django.urls import reverse
from encryption_compendium.test_utils import random_username, random_password, UnitTest
from research_assistant.models import User

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
