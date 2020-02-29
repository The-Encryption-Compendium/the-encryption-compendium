from django.urls import reverse
from encryption_compendium.test_utils import UnitTest
from unittest import skip


class LandingPageTestCase(UnitTest):
    """
    Tests for the site's landing page.
    """

    def test_templates(self):
        response = self.client.get(reverse("landing page"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "landing_page.html")
