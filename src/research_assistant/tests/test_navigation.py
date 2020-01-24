"""
Functional tests for the reesearch_assistant app
"""

from django.test import tag
from django.urls import reverse
from encryption_compendium.test_utils import (
    FunctionalTest,
    random_username,
    random_email,
    random_password,
)
from selenium.webdriver.common.keys import Keys

"""
---------------------------------------------------
Login tests
---------------------------------------------------
"""


@tag("auth", "login")
class FunctionalLoginTestCase(FunctionalTest):
    """
    Meepy the Anthropomorphic Router has an account on the site. She tries to
    login to her dashboard.
    """

    def setUp(self):
        super().setUp(create_user=True)

    def test_login_as_existing_user(self):
        # Meepy visits the login page of the site.
        self.browser.get(self.live_server_url + reverse("research login"))
        self.assertEqual(self.browser.title, "Login | The Encryption Compendium")

        # Meepy enters her username and password into the 'username' and
        # 'password' boxes.
        userbox = self.browser.find_element_by_id("id_username")
        passbox = self.browser.find_element_by_id("id_password")

        self.assertEqual(userbox.get_attribute("placeholder"), "Username")
        self.assertEqual(passbox.get_attribute("placeholder"), "Password")

        userbox.send_keys(self.username)
        passbox.send_keys(self.password)
        passbox.send_keys(Keys.ENTER)

        # Meepy is successfully logged in, and directed to her dashboard
        self.wait_for(lambda: self.assertIn("Dashboard", self.browser.title))


@tag("dashboard")
class FunctionalResearchDashboardTestCase(FunctionalTest):
    """
    Meepy logs in and checks her dashboard.
    """

    def test_redirect_to_login_if_unauthenticated(self):
        # Meepy forgets to log in before visiting the dashboard. She's redirected to
        # the login page.
        pass
