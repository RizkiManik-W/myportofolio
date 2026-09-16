from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import SkillForm
from main.models import Experience, Skill

def show_main(request):
    context = {
        "fullname" : "Putu Rizki Manik Widiadnyana",
        "name": "Rizki",
        "npm": "250662100",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "CS student at Universitas Indonesia, i love fun things that require creative thingking. Passionate about competitive programming, game development, and writting. I enjoy solving challanging problems, designing strategy-driven games, and all things thats related to creativity such as writting."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Rizki",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_skills(request):
    json_response = get_skills_json(request)

    skills = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    skills = [skill.object for skill in skills]

    context = {
        "name": "Rizki",
        "skills_list": skills,
        "title_query": request.GET.get("title", "").strip(),
    }
    return render(request, "skills.html", context)