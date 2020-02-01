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
        self.get_userbox = lambda: self.browser.find_element_by_id("id_username")
        self.get_passbox = lambda: self.browser.find_element_by_id("id_password")

    def test_login_as_existing_user(self):
        # Meepy visits the login page of the site.
        self.browser.get(self.live_server_url + reverse("research login"))
        self.assertEqual(self.browser.title, "Login | The Encryption Compendium")

        # Meepy enters her username and password into the 'username' and
        # 'password' boxes.
        userbox = self.get_userbox()
        passbox = self.get_passbox()

        self.assertEqual(userbox.get_attribute("placeholder"), "Username")
        self.assertEqual(passbox.get_attribute("placeholder"), "Password")

        userbox.send_keys(self.username)
        passbox.send_keys(self.password)
        passbox.send_keys(Keys.ENTER)

        # Meepy is successfully logged in, and directed to her dashboard
        self.wait_for(lambda: self.assertIn("Dashboard", self.browser.title))

    def test_invalid_login(self):
        # Meepy visits the login page, but enters the incorrect username.
        self.browser.get(self.live_server_url + reverse("research login"))
        initial_url = self.browser.current_url

        self.get_userbox().send_keys(random_username(self.rd))
        self.get_passbox().send_keys(self.password)
        self.get_passbox().send_keys(Keys.ENTER)

        self.wait_for(
            lambda: self.assertIn("Username does not exist.", self.browser.page_source)
        )
        self.assertEqual(self.browser.current_url, initial_url)

        # Meepy enters the correct username, but the incorrect password
        self.get_userbox().clear()
        self.get_userbox().send_keys(self.username)
        self.get_passbox().send_keys(random_password(self.rd))
        self.get_passbox().send_keys(Keys.ENTER)

        self.wait_for(
            lambda: self.assertIn(
                "Sorry, that login was invalid. Please try again.",
                self.browser.page_source,
            )
        )
        self.assertEqual(self.browser.current_url, initial_url)

        # Meepy enters the correct username and password, and logs in successfully
        self.get_passbox().send_keys(self.password)
        self.browser.find_element_by_id("login-button").click()

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
