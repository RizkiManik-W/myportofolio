from django.urls import path

from main.views import (
    create_skill,
    delete_skill,
    get_skills_json,
    show_experience,
    show_main,
    show_skills,
    update_skill,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("skills/", show_skills, name="show_skills"),
    path("skills/add/", create_skill, name="create_skill"),
    path("skills/<uuid:skill_id>/edit/", update_skill, name="update_skill"),
    path("skills/<uuid:skill_id>/delete/", delete_skill, name="delete_skill"),
    path("api/skills/", get_skills_json, name="get_skills_json"),
]