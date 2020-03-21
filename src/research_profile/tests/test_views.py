from django.contrib.auth import get_user
from django.test import tag
from django.urls import reverse
from encryption_compendium.test_utils import UnitTest
from entries.models import CompendiumEntry, CompendiumEntryTag
from users.models import User

from unittest import skip

# Create your tests here.
@tag("profile")
class DashboardTestCase(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)

    def test_compendium_entries_added_by_user_on_profile(self):
        self.client.login(username=self.username, password=self.password)
        # create some compendium entries with tags as user
        tags = ("test_tag_D", "test_tag_E", "test_tag_F")
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
        # get profile page
        response = self.client.get(reverse("research profile"))
        entries = response.context["entries"]
        for i, entry in enumerate(entries):
            # verify all entries added by the user are visible on this page
            self.assertEqual(entry["title"], tags[i])
            self.assertEqual(entry["tags"], tags[i])
            self.assertEqual(entry["url"], "https://www.example.com")
