from django.contrib.auth import get_user
from django.conf import settings
from django.core import mail
from django.test import tag
from django.urls import reverse
from encryption_compendium.test_utils import (
    random_email,
    random_username,
    random_password,
    UnitTest,
)
from research_assistant.models import (
    CompendiumEntry,
    CompendiumEntryTag,
    SignupToken,
    User,
    Author,
)
from unittest import skip
import datetime, random

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
    """
    Tests for the view to invite new users to join the site.
    """

    def setUp(self):
        super().setUp(preauth=True)
        self.user.is_staff = True
        self.user.save()
        self.new_user_email = random_email(self.rd)
        self.form_data = {"email": self.new_user_email, "create_user": ""}

    def test_page_uses_correct_templates(self):
        response = self.client.get(reverse("add new user"))
        self.assertTemplateUsed("base.html")
        self.assertTemplateUsed("dashboard_base.html")
        self.assertTemplateUsed("add_user.html")

    @tag("email")
    def test_add_new_user_to_site(self):
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(len(SignupToken.objects.all()), 0)

        # Have the staff user send a new email verification token to get
        # a new user signed up.
        response = self.client.post(reverse("add new user"), self.form_data)

        self.assertEqual(len(SignupToken.objects.all()), 1)
        tokens = SignupToken.objects.all()

        self.assertTrue(SignupToken.objects.filter(email=self.new_user_email).exists())

        # Check that the email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.new_user_email])

        # The page should say that we successfuly added a new user.
        self.assertIn("Your invite was sent!", response.content.decode("utf-8"))

    def test_only_staff_users_can_add_new_users(self):
        ### Only users that are staff members can send email verification tokens
        # Set User to be non-staff, and log the client back in
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        self.assertTrue(get_user(self.client).is_authenticated)

        # User should be redirected to the login page (which in turn will redirect
        # them to the dashboard).
        response = self.client.get(reverse("add new user"), follow=True)
        location, _ = response.redirect_chain[0]
        self.assertTrue(location.startswith(settings.LOGIN_URL))

        login_response = self.client.get(settings.LOGIN_URL, follow=True)
        self.assertEqual(response.redirect_chain[-1], login_response.redirect_chain[-1])

    def test_delete_invited_users_token(self):
        token = SignupToken.objects.create(email=self.new_user_email)
        self.assertTrue(SignupToken.objects.filter(email=self.new_user_email).exists())

        # Outstanding tokens should appear on the page
        response = self.client.get(reverse("add new user"))
        self.assertIn(self.new_user_email, response.content.decode("utf-8"))

        data = {"del_email": self.new_user_email}
        response = self.client.post(reverse("add new user"), data)
        self.assertFalse(SignupToken.objects.filter(email=self.new_user_email).exists())
        self.assertNotIn(self.new_user_email, response.content.decode("utf-8"))

    def test_cannot_send_token_when_outstanding_token_exists(self):
        token = SignupToken.objects.create(email=self.new_user_email)
        data = {"email": self.new_user_email, "create_user": ""}
        response = self.client.post(reverse("add new user"), data)

        self.assertEqual(len(SignupToken.objects.all()), 1)
        self.assertIn(
            "Signup token with this Email already exists.",
            response.content.decode("utf-8"),
        )


class SignupNewUserTest(UnitTest):
    """
    Tests for the sign up view that appears when a user tries to sign up
    using the link from their email invite.
    """

    def setUp(self):
        super().setUp()

        # Create a new email verification token
        self.token = SignupToken.objects.create(email=self.email)

    def test_sign_up_with_valid_token(self):
        # Ensure that the user we want to sign up as doesn't exist before
        # running tests
        self.assertFalse(User.objects.filter(username=self.username).exists())

        # Visit the signup page using a valid token
        url = self.token.signup_location
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("sign_up.html")

        # The email field should be default be populated with the email
        # corresponding to the provided token
        self.assertIn(self.token.email, response.content.decode("utf-8"))

        # Sign up as a new user to the site
        response = self.client.post(
            url,
            {
                "email": self.email,
                "username": self.username,
                "password": self.password,
                "password_2": self.password,
            },
        )
        self.assertTrue(User.objects.filter(username=self.username).exists())

    def test_cannot_sign_up_with_invalid_token(self):
        # If the token is invalid, we should get a 403 Forbidden response
        # from the server.
        url = self.token.signup_location
        self.token.delete()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_cannot_sign_up_without_any_token(self):
        # if there is no token passed as the parameter, we should get a 403 Forbidden response
        url = reverse("sign up")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


"""
---------------------------------------------------
Tests for user logout
---------------------------------------------------
"""


class LogoutTestCase(UnitTest):
    """
    Tests for the logout view.
    """

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

    def test_all_compendium_entries_visible_on_dashboard(self):
        # login as a user
        self.client.login(username=self.username, password=self.password)
        # create some compendium entries with tags as user
        tags = ("test_tag_A", "test_tag_B", "test_tag_C")
        for tagname in tags:
            if not CompendiumEntryTag.objects.filter(tagname=tagname).exists():
                CompendiumEntryTag.objects.create(tagname=tagname)
                tag_id = CompendiumEntryTag.objects.get(tagname=tagname).id
                data = {
                    "title": tagname,
                    "url": "https://www.example.com",
                    "tags": [tag_id],
                }
                self.new_entry_page = reverse("research new article")
                response = self.client.post(self.new_entry_page, data)
        response = self.client.get(reverse("research dashboard"))
        entries = response.context["entries"]
        for i, entry in enumerate(entries):
            self.assertEqual(entry["title"], tags[i])
            self.assertEqual(entry["tags"], tags[i])
            self.assertEqual(entry["url"], "https://www.example.com")
            self.assertEqual(entry["owner"], self.user)


"""
---------------------------------------------------
Tests for adding new tags and compendium entries
---------------------------------------------------
"""


@tag("compendium-entries")
class AddNewCompendiumEntryTestCase(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)
        self.new_entry_page = reverse("research new article")

        # Add three tags for testing purposes
        for tagname in ("test_tag_A", "test_tag_B", "test_tag_C"):
            if not CompendiumEntryTag.objects.filter(tagname=tagname).exists():
                CompendiumEntryTag.objects.create(tagname=tagname)

    def test_page_templates(self):
        # Ensure that the page uses the correct templates in its response
        response = self.client.get(self.new_entry_page)
        self.assertTemplateUsed("dashboard_base.html")
        self.assertTemplateUsed("new_article.html")

    @tag("tags")
    def test_add_new_compendium_entry(self):
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

        # Retrieve the tag ID for "test_tag_B"
        tag_id = CompendiumEntryTag.objects.get(tagname="test_tag_B").id

        # publisher information
        publisher = random_username(self.rd)

        # published date
        year = random.randrange(1900, datetime.date.today().year)
        month = random.randrange(1, 12)
        day = random.randrange(1, 31)

        # Send POST data to the URL to create a new entry and ensure that
        # the entry was created correctly.
        data = {
            "title": "New compendium entry",
            "abstract": "Abstract for new entry",
            "url": "https://example.com",
            "tags": [tag_id],
            "publisher_text": publisher,
            "year": year,
            "month": month,
            "day": day,
            "edit-entry": "",
        }
        response = self.client.post(self.new_entry_page, data)
        self.assertTrue(len(CompendiumEntry.objects.all()), 1)

        entry = CompendiumEntry.objects.get(title="New compendium entry")
        self.assertEqual(entry.owner, self.user)
        self.assertEqual(entry.title, "New compendium entry")
        self.assertEqual(entry.abstract, "Abstract for new entry")
        self.assertEqual(entry.url, "https://example.com")
        self.assertEqual(len(entry.tags.all()), 1)
        self.assertEqual(entry.tags.get().tagname, "test_tag_B")
        self.assertEqual(entry.publisher.publishername, publisher)
        self.assertEqual(entry.year, year)
        self.assertEqual(entry.month, month)
        self.assertEqual(entry.day, day)

    @tag("tags")
    def test_add_compendium_entry_with_multiple_tags(self):
        """Create a CompendiumEntry with multiple tags"""
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

        # Retrieve tag IDs for "test_tag_B" and "test_tag_C"
        id_A = CompendiumEntryTag.objects.get(tagname="test_tag_A").id
        id_C = CompendiumEntryTag.objects.get(tagname="test_tag_C").id

        # Send POST data with multiple tag IDs
        data = {
            "title": "New compendium entry",
            "tags": [id_A, id_C],
            "edit-entry": "",
        }
        self.client.post(self.new_entry_page, data)
        self.assertEqual(len(CompendiumEntry.objects.all()), 1)

        entry = CompendiumEntry.objects.get(title="New compendium entry")
        self.assertEqual(len(entry.tags.all()), 2)
        self.assertTrue(entry.tags.filter(tagname="test_tag_A").exists())
        self.assertFalse(entry.tags.filter(tagname="test_tag_B").exists())
        self.assertTrue(entry.tags.filter(tagname="test_tag_C").exists())

    def test_attempt_to_create_entry_with_empty_title(self):
        """New entries must have a title"""
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)
        tag_id = CompendiumEntryTag.objects.get(tagname="test_tag_A").id

        ### Try to create an entry without a title
        data = {
            "tags": [tag_id],
        }
        response = self.client.post(self.new_entry_page, data)
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

        ### Try to create an entry with an empty title
        data = {
            "title": "",
            "tags": [tag_id],
        }
        response = self.client.post(self.new_entry_page, data)
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

    def test_attempt_to_create_entry_without_tags(self):
        """New entries must have _at least_ one tag"""
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

        data = {
            "title": "New compendium entry",
        }
        self.client.post(self.new_entry_page, data)
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)


@tag("compendium-entries", "tags")
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


"""
---------------------------------------------------
Tests for modifying user settings
---------------------------------------------------
"""


class ChangePasswordViewTests(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)
        self.url = reverse("research settings")
        self.response = self.client.get(self.url)

    def test_password_change_should_logout(self):
        new_password = random_password(self.rd)

        # change user's password
        response = self.client.post(
            self.url,
            {
                "oldpassword": self.password,
                "newpassword1": new_password,
                "newpassword2": new_password,
            },
        )
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_trying_wrong_password(self):
        new_password = random_password(self.rd)

        # change user's password
        response = self.client.post(
            self.url,
            {
                "oldpassword": random_password(self.rd),
                "newpassword1": new_password,
                "newpassword2": new_password,
            },
        )
        self.assertTrue(get_user(self.client).is_authenticated)


@tag("Edit", "Delete")
class EditAndDeleteTests(UnitTest):
    """
    Tests for two views in the site:
    - The view for editing existing compendium entries.
    - The view for deleting entries.
    """

    def setUp(self):
        super().setUp(preauth=True)

        # Create some compendium entries as user 1
        test_tag = CompendiumEntryTag.objects.create(tagname="test_tag")
        test_author = Author.objects.create(authorname="test_author")
        self.data = {
            "title": "test article",
            "url": "https://www.example.com",
            "edit-entry": "",
            "tags": [test_tag.id],
            "authors": [test_author.id],
        }
        self.create_compendium_entries(self.data, 3)
        self.client.logout()

        # Create a second user, and add some entries as that user
        email2 = random_email(self.rd)
        username2 = random_username(self.rd)
        password2 = random_password(self.rd)
        self.user2 = User.objects.create_user(
            email=email2, username=username2, password=password2
        )
        self.client.force_login(self.user2)
        self.create_compendium_entries(self.data, 3)

    """
    Internal helper functions
    """

    def create_compendium_entries(self, data, num_of_entries):
        for _ in range(num_of_entries):
            new_entry_page = reverse("research new article")
            response = self.client.post(new_entry_page, data)

    """
    Tests
    """

    def test_compendium_entries_list_for_edit(self):
        # get list-my-entries page
        response = self.client.get(reverse("list my entries"))
        entries = response.context["entries"]
        for entry in entries:
            # verify all entries added by the user are visible on this page
            self.assertEqual(entry["title"], "test article")
            self.assertEqual(entry["url"], "https://www.example.com")
            self.assertEqual(entry["tags"], "test_tag")

    def test_delete_own_entry(self):
        # currently logged in as user2
        # test deleting entry that belongs to the user2
        entry_id = CompendiumEntry.objects.filter(owner=self.user2).first().id
        response = self.client.post(reverse("list my entries"), {"entry_id": entry_id})
        self.assertNotEqual(
            CompendiumEntry.objects.filter(owner=self.user).first().id, entry_id
        )

    def test_delete_others_entry(self):
        # currently logged in as user2
        # test deleting entry with owner user1
        entry_id = CompendiumEntry.objects.filter(owner=self.user).first().id
        data = {"entry_id": entry_id}
        response = self.client.post(reverse("list my entries"), data)
        self.assertEqual(
            CompendiumEntry.objects.filter(owner=self.user).first().id, entry_id
        )

    def test_edit_own_form(self):
        # currently logged in as user2
        # test edit entry that belongs to the user2
        entry_id = CompendiumEntry.objects.filter(owner=self.user2).first().id
        data = self.data.copy()
        data["title"] = "change article"
        data["publisher"] = random_username(self.rd)

        response = self.client.post(
            reverse("edit my entries") + "/" + str(entry_id), data
        )
        self.assertEqual(
            CompendiumEntry.objects.filter(id=entry_id).first().title, "change article"
        )

    def test_edit_others(self):
        # currently logged in as user2
        # test edit entry that belongs to the user1
        entry_id = CompendiumEntry.objects.filter(owner=self.user).first().id
        response = self.client.post(
            f"{reverse('edit my entries')}/{entry_id}", self.data
        )
        self.assertNotEqual(
            CompendiumEntry.objects.filter(id=entry_id).first().title, "change article"
        )
