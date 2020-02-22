"""
Functional tests for the research_settings app
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
Password change tests
---------------------------------------------------
"""


@tag("auth", "password-change")
class FunctionalPasswordChangeTests(FunctionalTest):
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

        menu = navbar.find_element_by_id("user-settings-dropdown-menu")
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
