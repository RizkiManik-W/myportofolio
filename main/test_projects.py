from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from main.models import ActivityLog, Project

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


class ProjectTestBase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="test-password")
        self.viewer = User.objects.create_user(username="viewer", password="test-password")
        self.other = User.objects.create_user(username="other", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio Website",
            description="Django site",
            tech_stack="Django, Python",
        )
        self.valid_data = {
            "title": "New Project",
            "description": "Does things",
            "tech_stack": "Python",
            "project_url": "https://github.com/example/project",
            "project_image_url": "",
        }


class ProjectStarTests(ProjectTestBase):
    def setUp(self):
        super().setUp()
        self.star_url = reverse("main:toggle_project_star", args=[self.project.pk])

    def test_user_can_star_and_unstar_without_removing_other_users(self):
        self.project.starred_by.add(self.other)
        self.client.force_login(self.viewer)

        response = self.client.post(self.star_url, **AJAX)
        self.assertEqual(response.json(), {"success": True, "is_starred": True, "star_count": 2})

        response = self.client.post(self.star_url, **AJAX)
        self.assertEqual(response.json(), {"success": True, "is_starred": False, "star_count": 1})
        self.assertTrue(self.project.starred_by.filter(pk=self.other.pk).exists())

    def test_anonymous_user_cannot_star(self):
        response = self.client.post(self.star_url, **AJAX)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_get_does_not_change_stars(self):
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_star_request_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.viewer)
        csrf_client.get(reverse("main:show_project"))

        self.assertEqual(csrf_client.post(self.star_url, **AJAX).status_code, 403)
        token = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(self.star_url, {"csrfmiddlewaretoken": token}, **AJAX)
        self.assertTrue(response.json()["is_starred"])


class ProjectApiTests(ProjectTestBase):
    def test_api_returns_public_count_and_user_specific_status(self):
        self.project.starred_by.add(self.viewer)
        api_url = reverse("main:get_projects_json")

        fields = self.client.get(api_url).json()[0]["fields"]
        self.assertEqual(fields["star_count"], 1)
        self.assertFalse(fields["is_starred"])
        self.assertEqual(fields["starred_by_names"], "viewer")

        self.client.force_login(self.viewer)
        self.assertTrue(self.client.get(api_url).json()[0]["fields"]["is_starred"])
        self.client.force_login(self.other)
        self.assertFalse(self.client.get(api_url).json()[0]["fields"]["is_starred"])

    def test_api_filters_by_title(self):
        Project.objects.create(title="Chess Engine", description="Plays chess")
        data = self.client.get(reverse("main:get_projects_json"), {"title": "chess"}).json()
        self.assertEqual([item["fields"]["title"] for item in data], ["Chess Engine"])


class ProjectPageTests(ProjectTestBase):
    def test_page_is_loaded_via_api_not_server_rendered(self):
        response = self.client.get(reverse("main:show_project"))
        self.assertContains(response, 'data-list-url="%s"' % reverse("api:project-list"))
        self.assertNotContains(response, "Portfolio Website")

    def test_controls_depend_on_role(self):
        url = reverse("main:show_project")

        anonymous = self.client.get(url)
        self.assertNotContains(anonymous, 'data-action="star"')
        self.assertNotContains(anonymous, 'id="project-dialog"')

        self.client.force_login(self.viewer)
        regular = self.client.get(url)
        self.assertContains(regular, 'data-action="star"')
        self.assertNotContains(regular, 'data-action="delete"')
        self.assertNotContains(regular, 'data-action="edit"')

        self.client.force_login(self.admin)
        admin = self.client.get(url)
        self.assertContains(admin, 'data-action="delete"')
        self.assertContains(admin, 'data-action="edit"')
        self.assertContains(admin, 'id="open-project-dialog"')

    def test_page_sets_csrf_cookie_for_regular_users(self):
        self.client.force_login(self.viewer)
        response = self.client.get(reverse("main:show_project"))
        self.assertIn("csrftoken", response.cookies)


class ProjectWriteTests(ProjectTestBase):
    def test_admin_can_create_via_ajax_and_is_logged(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("main:create_project"), self.valid_data, **AJAX)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(title="New Project").exists())
        self.assertTrue(ActivityLog.objects.filter(action="create", target_type="project").exists())

    def test_create_returns_field_errors_as_json(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("main:create_project"), {**self.valid_data, "project_url": "nope"}, **AJAX
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("project_url", response.json()["errors"])

    def test_create_strips_html_from_title(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("main:create_project"), {**self.valid_data, "title": "<b>Bold</b>"}, **AJAX
        )
        self.assertTrue(Project.objects.filter(title="Bold").exists())

    def test_regular_user_cannot_create(self):
        self.client.force_login(self.viewer)
        response = self.client.post(reverse("main:create_project"), self.valid_data, **AJAX)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_admin_can_update_via_ajax(self):
        self.client.force_login(self.admin)
        url = reverse("main:update_project", args=[self.project.pk])
        response = self.client.post(url, self.valid_data, **AJAX)
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "New Project")

    def test_regular_user_cannot_update(self):
        self.client.force_login(self.viewer)
        url = reverse("main:update_project", args=[self.project.pk])
        self.assertEqual(self.client.post(url, self.valid_data, **AJAX).status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio Website")

    def test_admin_can_delete_via_ajax(self):
        self.client.force_login(self.admin)
        url = reverse("main:delete_project", args=[self.project.pk])
        response = self.client.post(url, **AJAX)
        self.assertEqual(response.json()["success"], True)
        self.assertFalse(Project.objects.exists())
        self.assertTrue(ActivityLog.objects.filter(action="delete", target_type="project").exists())

    def test_regular_user_cannot_delete(self):
        self.client.force_login(self.viewer)
        url = reverse("main:delete_project", args=[self.project.pk])
        self.assertEqual(self.client.post(url, **AJAX).status_code, 403)
        self.assertTrue(Project.objects.exists())

    def test_delete_rejects_get(self):
        self.client.force_login(self.admin)
        url = reverse("main:delete_project", args=[self.project.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertTrue(Project.objects.exists())
