from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Experience


class ExperienceStarTests(TestCase):
    def setUp(self):
        self.viewer = User.objects.create_user(username="viewer", password="test-password")
        self.other = User.objects.create_user(username="other", password="test-password")
        self.experience = Experience.objects.create(title="Internship", description="Building apps")
        self.star_url = reverse("main:toggle_experience_star", args=[self.experience.pk])
        self.ajax = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}

    def test_regular_user_can_star_and_unstar_without_removing_other_users(self):
        self.experience.starred_by.add(self.other)
        self.client.force_login(self.viewer)

        response = self.client.post(self.star_url, **self.ajax)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "is_starred": True, "star_count": 2})
        self.assertTrue(self.experience.starred_by.filter(pk=self.viewer.pk).exists())

        response = self.client.post(self.star_url, **self.ajax)
        self.assertEqual(response.json(), {"success": True, "is_starred": False, "star_count": 1})
        self.assertFalse(self.experience.starred_by.filter(pk=self.viewer.pk).exists())
        self.assertTrue(self.experience.starred_by.filter(pk=self.other.pk).exists())

    def test_anonymous_user_cannot_star(self):
        response = self.client.post(self.star_url, **self.ajax)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_get_does_not_change_stars(self):
        self.client.force_login(self.viewer)
        response = self.client.get(self.star_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_api_returns_public_count_and_user_specific_status(self):
        self.experience.starred_by.add(self.viewer)
        api_url = reverse("main:get_experiences_json")
        fields = self.client.get(api_url).json()[0]["fields"]
        self.assertEqual(fields["star_count"], 1)
        self.assertFalse(fields["is_starred"])
        self.assertEqual(fields["starred_by_names"], "viewer")

        self.client.force_login(self.viewer)
        self.assertTrue(self.client.get(api_url).json()[0]["fields"]["is_starred"])
        self.client.force_login(self.other)
        self.assertFalse(self.client.get(api_url).json()[0]["fields"]["is_starred"])

    def test_star_controls_are_available_to_regular_users(self):
        page_url = reverse("main:show_experience")
        anonymous_page = self.client.get(page_url)
        self.assertContains(anonymous_page, 'class="star-count"')
        self.assertNotContains(anonymous_page, 'class="experience-star-form"')

        self.client.force_login(self.viewer)
        signed_in_page = self.client.get(page_url)
        self.assertContains(signed_in_page, 'class="experience-star-form"')
        self.assertNotContains(signed_in_page, 'class="experience-delete-form"')
        self.assertNotContains(signed_in_page, 'data-update-url=')

    def test_star_request_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.viewer)
        csrf_client.get(reverse("main:show_experience"))

        self.assertEqual(csrf_client.post(self.star_url, **self.ajax).status_code, 403)
        self.assertEqual(self.experience.starred_by.count(), 0)

        token = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(self.star_url, {"csrfmiddlewaretoken": token}, **self.ajax)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_starred"])
