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

    """
    Helper functions
    """

    def get_userbox(self):
        return self.browser.find_element_by_id("id_username")

    def get_passbox(self):
        return self.browser.find_element_by_id("id_password")

    def go_to_login_page(self):
        self.browser.get(self.live_server_url + reverse("research login"))

    """
    Tests
    """

    def test_login_as_existing_user(self):
        # Meepy visits the login page of the site.
        self.go_to_login_page()
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

        # Now if she tries to go back to the login page, she's redirected back to
        # her dashboard.
        self.go_to_login_page()
        self.wait_for(lambda: self.assertIn("Dashboard", self.browser.title))

    def test_invalid_login(self):
        # Meepy visits the login page, but enters the incorrect username.
        self.go_to_login_page()
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
        self.get_userbox().clear()
        self.get_userbox().send_keys(self.username)
        self.get_passbox().send_keys(self.password)
        self.get_passbox().send_keys(Keys.ENTER)

        self.wait_for(lambda: self.assertIn("Dashboard", self.browser.title))

    def test_redirect_to_login_if_unauthenticated(self):
        # Meepy forgets to log in before visiting the dashboard. She's redirected to
        # the login page.
        pass

    def test_logout(self):
        # Meepy logs in to the site.
        self.go_to_login_page()
        self.get_userbox().send_keys(self.username)
        self.get_passbox().send_keys(self.password)
        self.browser.find_element_by_id("login-button").click()

        self.wait_for(lambda: self.assertIn("Dashboard", self.browser.title))

        # Meepy clicks the profile button in the navbar, and then clicks the logout
        # button.
        # Use the execute_script() function instead of directly clicking the logout button,
        # since otherwise we can run into "element cannot be scrolled into view" errors.
        navbar = self.browser.find_element_by_id("navbar")
        profile_button = navbar.find_element_by_id("user-profile-dropdown-button")
        self.browser.execute_script("arguments[0].click();", profile_button)

        menu = navbar.find_element_by_id("user-settings-dropdown-menu")
        logout_button = menu.find_element_by_id("logout-button")
        self.browser.execute_script("arguments[0].click();", logout_button)

        self.wait_for(lambda: self.assertIn("Login", self.browser.title))


"""
---------------------------------------------------
Dashboard tests
---------------------------------------------------
"""


@tag("dashboard")
class FunctionalResearchDashboardTestCase(FunctionalTest):
    """
    Meepy logs in and checks her dashboard.
    """

    def setUp(self):
        super().setUp(create_user=True, preauth=True)

    def test_new_article_link_in_dashboard(self):
        # Meepy wants to add a new article to the compendium
        # Meepy visits her dashboard
        self.browser.get(self.live_server_url + reverse("research dashboard"))
        self.assertEqual(self.browser.title, "Dashboard | The Encryption Compendium")

        # She notices a "Add new article" link and clicks it
        self.browser.find_element_by_link_text("Add new compendium entry").click()

        self.assertEqual(self.browser.title, "New Article | The Encryption Compendium")

    def test_new_article_form(self):
        # Meepy fills in the form for new article
        self.browser.get(self.live_server_url + reverse("research new article"))
        inputbox = self.browser.find_element_by_id("id_title")
        inputbox.send_keys("Test article")
        inputbox = self.browser.find_element_by_id("id_abstract")
        inputbox.send_keys("Abstract for test article")
        inputbox = self.browser.find_element_by_id("id_url")
        inputbox.send_keys("https://www.google.com")
        inputbox = self.browser.find_element_by_id("id_tags")
        inputbox.send_keys("test, ignore_article, article_ignore")
        self.browser.find_element_by_tag_name("button").click()

        self.assertEqual(self.browser.title, "Dashboard | The Encryption Compendium")
