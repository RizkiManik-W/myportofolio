from django.shortcuts import render

from main.models import Experience


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
        "name": "Burhan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)