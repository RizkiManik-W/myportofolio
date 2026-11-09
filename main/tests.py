import uuid

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import ActivityLog, Experience, Project, Skill


class MainTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            password="test-password",
        )
        self.client.force_login(self.admin)
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page_uses_ajax_grid_and_api_data(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, 'id="experience-grid"')
        self.assertContains(
            response,
            f'data-api-url="{reverse("main:get_experiences_json")}"',
        )
        self.assertContains(response, "/static/js/experiences.js")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        # JavaScript replaces this UUID in the card template with the API pk.
        placeholder = "00000000-0000-0000-0000-000000000000"
        self.assertContains(
            response,
            f'data-update-url="{reverse("main:update_experience", args=[placeholder])}"',
        )
        self.assertContains(
            response,
            f'action="{reverse("main:delete_experience", args=[placeholder])}"',
        )

        api_response = self.client.get(reverse("main:get_experiences_json"))
        self.assertEqual(api_response.status_code, 200)
        data = api_response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["pk"], str(self.experience.pk))
        fields = data[0]["fields"]
        self.assertEqual(fields["title"], self.experience.title)
        self.assertEqual(fields["description"], self.experience.description)
        self.assertEqual(fields["category_display"], "Part-Time")
        self.assertTrue(fields["is_ongoing"])
        self.assertIsNone(fields["ended_at"])

    def test_empty_experience_page_uses_ajax_grid_and_empty_api_response(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="experience-grid"')
        self.assertContains(response, "Loading experience...")
        self.assertNotContains(response, "Belum ada pengalaman yang ditambahkan.")

        api_response = self.client.get(reverse("main:get_experiences_json"))
        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(api_response.json(), [])

    def test_completed_experience_is_available_to_ajax(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        response = self.client.get(reverse("main:get_experiences_json"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(response.status_code, 200)
        fields = response.json()[0]["fields"]
        self.assertFalse(fields["is_ongoing"])
        self.assertEqual(fields["ended_at"], self.experience.ended_at.isoformat())

    def test_experience_search_filters_api_by_title(self):
        Experience.objects.create(
            title="Frontend Intern",
            description="Built UI mockups.",
            category="internship",
        )

        page_response = self.client.get(
            reverse("main:show_experience"), {"title": "asisten"},
        )
        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, 'value="asisten"')

        response = self.client.get(
            reverse("main:get_experiences_json"), {"title": "asisten"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["fields"]["title"] for item in response.json()],
            [self.experience.title],
        )

    def test_skill_url_uses_skills_template(self):
        response = self.client.get(reverse("main:show_skills"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "skills.html")

    def test_skill_model_data_is_available_to_ajax_skill_list(self):
        skill = Skill.objects.create(
            title="Competitive Programming",
            description="Solving algorithmic problems for fun.",
            category="programming",
            order=1,
        )

        self.assertEqual(str(skill), "Competitive Programming")

        page_response = self.client.get(reverse("main:show_skills"))
        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, 'id="skills-grid"')
        self.assertContains(page_response, "/static/js/skills.js")
        self.assertNotContains(page_response, skill.title)

        api_response = self.client.get(reverse("main:get_skills_json"))
        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(api_response.json()[0]["fields"]["title"], skill.title)
        self.assertEqual(api_response.json()[0]["fields"]["description"], skill.description)

    def test_empty_skills_page_uses_ajax_grid_and_empty_api_response(self):
        Skill.objects.all().delete()

        page_response = self.client.get(reverse("main:show_skills"))
        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, 'id="skills-grid"')
        self.assertNotContains(page_response, "Belum ada skill yang ditambahkan.")

        api_response = self.client.get(reverse("main:get_skills_json"))
        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(api_response.json(), [])

    def test_delete_experience_removes_existing_experience(self):
        response = self.client.post(reverse("main:delete_experience", args=[self.experience.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_update_experience_form_updates_existing_experience(self):
        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.pk]),
            {
                "title": "Updated PBP Assistant",
                "description": "Updated experience description.",
                "category": "research",
                "thumbnail": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Updated PBP Assistant")
        self.assertEqual(self.experience.category, "research")

    def test_update_skill_form_updates_existing_skill(self):
        skill = Skill.objects.create(
            title="Python",
            description="Programming language for backend work.",
            category="programming",
            proficiency="Advanced",
            order=1,
        )

        response = self.client.post(
            reverse("main:update_skill", args=[skill.pk]),
            {
                "title": "Python & Django",
                "description": "Updated backend and web development skill.",
                "category": "web",
                "proficiency": "Expert",
                "order": 2,
            },
        )

        self.assertEqual(response.status_code, 302)
        skill.refresh_from_db()
        self.assertEqual(skill.title, "Python & Django")
        self.assertEqual(skill.category, "web")
        self.assertEqual(skill.proficiency, "Expert")
        self.assertEqual(skill.order, 2)

    def test_authenticated_user_can_toggle_skill_star(self):
        skill = Skill.objects.create(
            title="Python",
            description="Programming language for backend work.",
            category="programming",
            order=1,
        )

        star_url = reverse("main:toggle_skill_star", args=[skill.pk])

        response = self.client.post(star_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(skill.starred_by.filter(pk=self.admin.pk).exists())

        self.client.post(star_url)
        self.assertFalse(skill.starred_by.filter(pk=self.admin.pk).exists())

    def test_skills_api_uses_username_for_starred_user(self):
        skill = Skill.objects.create(
            title="Python",
            description="Programming language for backend work.",
            category="programming",
            order=1,
        )
        skill.starred_by.add(self.admin)

        response = self.client.get(reverse("main:get_skills_json"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"starred_by": [["admin"]]')


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


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(
                self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(
                self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")
        self.assertEqual(self.project.description, "My website")

        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "visitor")
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_star_rejects_get(self):
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_staff_without_editor_group_cannot_manage(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_can_patch_but_not_create_or_delete(self):
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)

        response = self.client.patch(self.detail_url, {"title": "Edited"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Edited")

        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_writes_are_recorded_in_activity_log(self):
        self.client.force_authenticate(user=self.owner)
        created = self.client.post(self.list_url, self.payload, format="json")
        url = reverse("api:project-detail", args=[created.data["id"]])
        self.client.patch(url, {"title": "Renamed"}, format="json")
        self.client.delete(url)
        actions = list(
            ActivityLog.objects.filter(target_type="project")
            .order_by("created_at", "id").values_list("action", flat=True)
        )
        self.assertEqual(actions, ["create", "update", "delete"])

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SkillAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password="test-password",
        )
        self.member = User.objects.create_user(
            username="member", password="test-password",
        )
        self.editor = User.objects.create_user(
            username="editor", password="test-password",
        )
        self.editor.groups.add(Group.objects.create(name="Editor"))

        self.skill = Skill.objects.create(
            title="Python",
            description="Building useful tools",
            category="programming",
            proficiency="Intermediate",
            order=1,
        )
        self.list_url = reverse("api:skill-list")
        self.detail_url = reverse(
            "api:skill-detail", args=[self.skill.id],
        )
        self.payload = {
            "title": "Django",
            "description": "Building web applications",
            "category": "web",
            "proficiency": "Intermediate",
            "order": 2,
        }

    def test_every_role_can_read(self):
        for user in (None, self.member, self.editor, self.owner):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)

                response = self.client.get(self.list_url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data[0]["id"], str(self.skill.id))

                response = self.client.get(self.detail_url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data["title"], "Python")

    def test_guest_and_member_cannot_write(self):
        for user in (None, self.member):
            self.client.force_authenticate(user=user)

            for method, url, data in [
                ("post", self.list_url, self.payload),
                ("put", self.detail_url, self.payload),
                ("patch", self.detail_url, {"title": "Forbidden"}),
                ("delete", self.detail_url, {}),
            ]:
                with self.subTest(user=str(user), method=method):
                    response = getattr(self.client, method)(
                        url, data, format="json",
                    )
                    self.assertEqual(response.status_code, 403)

                    # A rejection must leave the database unchanged.
                    self.assertEqual(Skill.objects.count(), 1)
                    self.skill.refresh_from_db()
                    for field, expected in {
                        "title": "Python",
                        "description": "Building useful tools",
                        "category": "programming",
                        "proficiency": "Intermediate",
                        "order": 1,
                    }.items():
                        self.assertEqual(
                            getattr(self.skill, field), expected,
                        )

    def test_editor_can_patch_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            self.detail_url, {"title": "Edited Python"}, format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.title, "Edited Python")
        self.assertEqual(self.skill.description, "Building useful tools")

        before = Skill.objects.values().get(pk=self.skill.pk)

        response = self.client.post(
            self.list_url, self.payload, format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Skill.objects.count(), 1)
        self.assertEqual(
            Skill.objects.values().get(pk=self.skill.pk), before,
        )

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Skill.objects.count(), 1)
        self.assertEqual(
            Skill.objects.values().get(pk=self.skill.pk), before,
        )

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url, self.payload, format="json",
        )
        self.assertEqual(response.status_code, 201)
        created = Skill.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, "Django")
        self.assertEqual(Skill.objects.count(), 2)

        url = reverse("api:skill-detail", args=[created.pk])
        response = self.client.patch(
            url, {"title": "Updated Django"}, format="json",
        )
        self.assertEqual(response.status_code, 200)
        created.refresh_from_db()
        self.assertEqual(created.title, "Updated Django")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Skill.objects.filter(pk=created.pk).exists())
        self.assertEqual(Skill.objects.count(), 1)

    def test_invalid_input_is_rejected_without_changes(self):
        self.client.force_authenticate(user=self.owner)
        before = Skill.objects.values().get(pk=self.skill.pk)

        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": "<br>"}, "title"),
            ({"description": "<br>"}, "description"),
            ({"category": "invalid-category"}, "category"),
            ({"order": 0}, "order"),
        ]:
            with self.subTest(field=field, changes=changes):
                response = self.client.post(
                    self.list_url,
                    {**self.payload, **changes},
                    format="json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.assertEqual(Skill.objects.count(), 1)

                response = self.client.patch(
                    self.detail_url, changes, format="json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.assertEqual(
                    Skill.objects.values().get(pk=self.skill.pk),
                    before,
                )

    def test_text_is_cleaned_before_saving(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "title": " <b>Django</b> ",
                "description": " <p>Web applications</p> ",
                "proficiency": " <i>Intermediate</i> ",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        created = Skill.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, "Django")
        self.assertEqual(created.description, "Web applications")
        self.assertEqual(created.proficiency, "Intermediate")

    def test_guest_cannot_star(self):
        url = reverse("api:skill-star", args=[self.skill.pk])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.skill.starred_by.count(), 0)

    def test_logged_in_roles_can_toggle_their_own_star(self):
        url = reverse("api:skill-star", args=[self.skill.pk])

        for user in (self.member, self.editor, self.owner):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)

                response = self.client.post(url)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data["is_starred"])
                self.assertEqual(response.data["star_count"], 1)
                self.assertEqual(
                    list(self.skill.starred_by.values_list("pk", flat=True)),
                    [user.pk],
                )

                response = self.client.post(url)
                self.assertEqual(response.status_code, 200)
                self.assertFalse(response.data["is_starred"])
                self.assertEqual(response.data["star_count"], 0)
                self.assertEqual(self.skill.starred_by.count(), 0)

    def test_star_fields_cannot_be_forged_on_creation(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 999,
                "is_starred": True,
                "starred_by": [self.member.pk],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

        created = Skill.objects.get(pk=response.data["id"])
        self.assertEqual(created.starred_by.count(), 0)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(username="owner", password="test-password")
        )

        response = client.post(
            self.list_url, self.payload, format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Skill.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(username="owner", password="test-password")
        )

        # The Skills page renders csrf_token for the logged-in owner.
        page = client.get(reverse("main:show_skills"))
        self.assertEqual(page.status_code, 200)
        token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Skill.objects.filter(pk=response.data["id"]).exists()
        )
