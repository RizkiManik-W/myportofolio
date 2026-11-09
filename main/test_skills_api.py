from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Skill


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