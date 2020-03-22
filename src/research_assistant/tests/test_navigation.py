"""
Functional tests for the reesearch_assistant app
"""

from django.core import mail
from django.test import tag
from django.urls import reverse
from utils.test_utils import (
    FunctionalTest,
    random_username,
    random_email,
    random_password,
)
from users.models import SignupToken, User
from selenium.webdriver.common.keys import Keys
from unittest import skip

"""
---------------------------------------------------
Login tests
---------------------------------------------------
"""


@tag("auth", "login")
class LoginFunctionalTestCase(FunctionalTest):
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
        self.get_passbox().clear()
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
        # Use the execute_script() function instead of directly clicking the logout
        # button, since otherwise we can run into "element cannot be scrolled into
        # view" errors.
        navbar = self.browser.find_element_by_id("navbar")
        profile_button = navbar.find_element_by_id("user-profile-dropdown-button")
        self.browser.execute_script("arguments[0].click();", profile_button)

        menu = navbar.find_element_by_id("user-profile-dropdown-menu")
        logout_button = menu.find_element_by_id("logout-button")
        self.browser.execute_script("arguments[0].click();", logout_button)

        self.wait_for(lambda: self.assertIn("Login", self.browser.title))


"""
---------------------------------------------------
Signup tests
---------------------------------------------------
"""


@tag("auth")
class InviteUserFunctionalTestCase(FunctionalTest):
    """
    Functional tests for inviting a new user to the site using a signup token.
    """

    def setUp(self):
        super().setUp(preauth=True)
        self.user.is_staff = True
        self.user.save()

    def test_invite_new_user_to_site(self):
        # Check that database hasn't been modified in a way that would interfere
        # with the tests.
        self.assertEquals(len(mail.outbox), 0)

        # Meepy, a staff member on the site, goes to the page to invite a new user
        self.browser.get(f"{self.live_server_url}{reverse('research dashboard')}")
        self.wait_for(lambda: self.assertIn("Dashboard", self.browser.title))
        self.browser.find_element_by_id("invite_user_button").click()
        self.wait_for(lambda: self.assertIn("Invite new user", self.browser.title))

        # She enters the email address for a new user into the 'email' input
        new_user_email = random_email(self.rd)
        self.browser.find_element_by_id("id_email").send_keys(new_user_email)
        self.browser.find_element_by_id("new_user_submit_button").click()

        # The site creates a new SignupToken for the provided email address, and
        # sends an email to the invited user.
        self.wait_for(
            lambda: self.assertTrue(
                SignupToken.objects.filter(email=new_user_email).exists()
            )
        )
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, [new_user_email])


@tag("auth")
class SignupFunctionalTestCase(FunctionalTest):
    """
    Use a valid signup token to sign up as a new user to the site.
    """

    def setUp(self):
        super().setUp()

        # Generate a signup token for a new user
        self.token = SignupToken.objects.create(email=self.email)

    def test_sign_up_with_valid_token(self):
        # Meepy receives an email with URL that allows her to sign up
        # as a new user to the site. She visits that URL.
        self.browser.get(f"{self.live_server_url}{self.token.signup_location}")
        self.assertIn("Sign up", self.browser.title)

        # In the email field, she sees the email to which the signup token
        # was sent.
        self.assertEqual(
            self.browser.find_element_by_id("id_email").get_attribute("value"),
            self.email,
        )

        # Meepy enters her details into the other fields of the form
        self.browser.find_element_by_id("id_username").send_keys(self.username)
        self.browser.find_element_by_id("id_password").send_keys(self.password)
        self.browser.find_element_by_id("id_password_2").send_keys(self.password)
        self.browser.find_element_by_id("signup-submit-button").click()

        # A new user is created for Meepy, and the token that was issued to her
        # is deleted.
        self.wait_for(
            lambda: self.assertTrue(
                User.objects.filter(username=self.username).exists()
            )
        )
        self.wait_for(
            lambda: self.assertFalse(
                SignupToken.objects.filter(email=self.email).exists()
            )
        )


"""
---------------------------------------------------
Dashboard tests
---------------------------------------------------
"""


@tag("dashboard")
class ResearchDashboardFunctionalTestCase(FunctionalTest):
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

        # She clicks on the dropdown
        self.browser.find_element_by_id("user-profile-dropdown-button").click()
        # then on My-entries link
        self.browser.find_element_by_id("my-entries").click()

        self.assertEqual(self.browser.title, "My entries | The Encryption Compendium")

        # Clicks Add new entry link
        self.browser.find_element_by_id("add-new-entry").click()
        self.assertEqual(self.browser.title, "New entry | The Encryption Compendium")

    @skip("TODO")
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
        self.browser.find_element_by_id("entry-submit-button").click()

        self.assertEqual(self.browser.title, "Dashboard | The Encryption Compendium")


"""
---------------------------------------------------
Account management tests
---------------------------------------------------
"""


@tag("auth", "password-change")
class PasswordChangeFunctionalTestCase(FunctionalTest):
    """
    Functional test suite for changing the user password
    """

    def setUp(self):
        super().setUp(preauth=True)

    """
    Meepy is logged-in and wants to change her password
    """

    def test_navigation_to_password_change_form(self):
        self.browser.get(self.live_server_url + reverse("research dashboard"))
        # Meepy clicks the profile button in the navbar, and then clicks the settings
        # button.
        navbar = self.browser.find_element_by_id("navbar")
        profile_button = navbar.find_element_by_id("user-profile-dropdown-button")
        self.browser.execute_script("arguments[0].click();", profile_button)

        menu = navbar.find_element_by_id("user-profile-dropdown-menu")
        settings_button = menu.find_element_by_id("user-settings")
        self.browser.execute_script("arguments[0].click();", settings_button)

        self.wait_for(lambda: self.assertIn("Settings", self.browser.title))

        # Meepy then clicks on change password link
        change_password_link = self.browser.find_element_by_id("change-password-link")
        self.browser.execute_script("arguments[0].click();", change_password_link)

        # Meepy enters her current and new password (twice) and she should be
        # logged out on successful change of password
        oldpass_box = self.browser.find_element_by_id("id_oldpassword")
        newpass1_box = self.browser.find_element_by_id("id_newpassword1")
        newpass2_box = self.browser.find_element_by_id("id_newpassword2")

        self.assertEqual(oldpass_box.get_attribute("placeholder"), "Your old Password")
        self.assertEqual(newpass1_box.get_attribute("placeholder"), "New Password")
        self.assertEqual(
            newpass2_box.get_attribute("placeholder"), "Confirm New Password"
        )

        newpass = random_password(self.rd)

        oldpass_box.send_keys(self.password)
        newpass1_box.send_keys(newpass)
        newpass2_box.send_keys(newpass)
        newpass2_box.send_keys(Keys.ENTER)

        self.wait_for(lambda: self.assertIn("Login", self.browser.title))
