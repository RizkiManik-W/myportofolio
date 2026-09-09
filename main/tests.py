from django.test import TestCase
from django.urls import reverse


class PortfolioHomepageTests(TestCase):
    def test_index_view_includes_required_profile_context(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("fullname", response.context)
        self.assertIn("name", response.context)
        self.assertIn("npm", response.context)
        self.assertIn("study_program", response.context)
        self.assertIn("bio", response.context)
