from django.urls import path

from main.views import (
    create_experience,
    create_skill,
    delete_experience,
    delete_skill,
    get_skills_json,
    login_user,
    logout_user,
    register,
    show_activity_log,
    show_experience,
    show_main,
    show_skills,
    toggle_skill_star,
    update_experience,
    update_skill,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("experience/", show_experience, name="show_experience"),
    path("activity/", show_activity_log, name="show_activity_log"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("skills/", show_skills, name="show_skills"),
    path("skills/<uuid:skill_id>/star/", toggle_skill_star, name="toggle_skill_star"),
    path("skills/add/", create_skill, name="create_skill"),
    path("skills/<uuid:skill_id>/edit/", update_skill, name="update_skill"),
    path("skills/<uuid:skill_id>/delete/", delete_skill, name="delete_skill"),
    path("api/skills/", get_skills_json, name="get_skills_json"),
]
