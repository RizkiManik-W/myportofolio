from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from main.models import Experience, Skill


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

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(
            response,
            f'href="{reverse("main:update_experience", args=[self.experience.pk])}"',
        )
        self.assertContains(
            response,
            f'action="{reverse("main:delete_experience", args=[self.experience.pk])}"',
        )

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_experience_search_filters_by_title(self):
        Experience.objects.create(
            title="Frontend Intern",
            description="Built UI mockups.",
            category="internship",
        )

        response = self.client.get(reverse("main:show_experience"), {"title": "Asisten"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asisten Dosen PBP")
        self.assertNotContains(response, "Frontend Intern")

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
