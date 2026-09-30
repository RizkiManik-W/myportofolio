from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ExperienceForm, SkillForm
from main.models import ActivityLog, Experience, Skill


def _is_editor(user):
    return user.is_authenticated and user.groups.filter(name="Editor").exists()


def _can_edit_portfolio(user):
    return user.is_superuser or _is_editor(user)


def _record_activity(user, action, target_type, target):
    ActivityLog.objects.create(
        actor=user,
        actor_username=user.get_username(),
        action=action,
        target_type=target_type,
        target_id=str(target.pk),
        target_title=target.title,
    )


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Rizki",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = redirect("main:show_main")
            response.set_cookie("last_login", user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "")
            return response
    else:
        form = AuthenticationForm(request)

    context = {
        "name": "Rizki",
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


def show_main(request):
    context = {
        "fullname" : "Putu Rizki Manik Widiadnyana",
        "name": "Rizki",
        "npm": "250662100",
        "study_program": "S1 Ilmu Komputer",
        "last_login": request.COOKIES.get(
            "last_login",
            "Belum ada sesi login / Cookie tidak ditemukan",
        ),
        "bio": (
            "CS student at Universitas Indonesia, i love fun things that require creative thingking. Passionate about competitive programming, game development, and writting. I enjoy solving challanging problems, designing strategy-driven games, and all things thats related to creativity such as writting."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    title_query = request.GET.get("title", "").strip()
    experience_list = Experience.objects.all()

    if title_query:
        experience_list = experience_list.filter(title__icontains=title_query)

    context = {
        "name": "Rizki",
        "experience_list": experience_list,
        "title_query": title_query,
        "can_edit": _can_edit_portfolio(request.user),
    }
    return render(request, "experience.html", context)


@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            experience = form.save()
            _record_activity(request.user, "create", "experience", experience)
        messages.success(request, "Experience added successfully.")
        return redirect("main:show_experience")

    context = {
        "name": "Rizki",
        "form": form,
        "is_editing": False,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not _can_edit_portfolio(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            experience = form.save()
            _record_activity(request.user, "update", "experience", experience)
        messages.success(request, "Experience updated successfully.")
        return redirect("main:show_experience")

    context = {
        "name": "Rizki",
        "form": form,
        "is_editing": True,
    }
    return render(request, "experience_form.html", context)


def show_skills(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skill.objects.prefetch_related("starred_by").order_by("order")
    if title_query:
        skills = skills.filter(title__icontains=title_query)

    context = {
        "name": "Rizki",
        "skills_list": skills,
        "skill_categories": Skill.SKILL_TYPES,
        "title_query": title_query,
        "can_edit": _can_edit_portfolio(request.user),
    }
    return render(request, "skills.html", context)


@login_required(login_url="/login/")
def show_activity_log(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    context = {
        "name": "Rizki",
        "activity_list": ActivityLog.objects.select_related("actor")[:100],
    }
    return render(request, "activity_log.html", context)


@login_required(login_url="/login/")
def toggle_skill_star(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        if request.user in skill.starred_by.all():
            skill.starred_by.remove(request.user)
        else:
            skill.starred_by.add(request.user)

    return redirect("main:show_skills")


@login_required(login_url="/login/")
def create_skill(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = SkillForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            skill = form.save()
            _record_activity(request.user, "create", "skill", skill)
        messages.success(request, "Skill added successfully.")
        return redirect("main:show_skills")

    context = {
        "name": "Rizki",
        "form": form,
        "is_editing": False,
    }
    return render(request, "skills_form.html", context)


@login_required(login_url="/login/")
def update_skill(request, skill_id):
    if not _can_edit_portfolio(request.user):
        raise PermissionDenied

    skill = get_object_or_404(Skill, pk=skill_id)
    form = SkillForm(request.POST or None, instance=skill)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            skill = form.save()
            _record_activity(request.user, "update", "skill", skill)
        messages.success(request, "Skill updated successfully.")
        return redirect("main:show_skills")

    context = {
        "name": "Rizki",
        "form": form,
        "is_editing": True,
    }
    return render(request, "skills_form.html", context)


def get_skills_json(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skill.objects.prefetch_related("starred_by").order_by("order")

    if title_query:
        skills = skills.filter(title__icontains=title_query)

    data = []
    for skill in skills:
        starred_users = list(skill.starred_by.all())
        data.append({
            "pk": str(skill.pk),
            "fields": {
                "title": skill.title,
                "description": skill.description,
                "category": skill.category,
                "proficiency": skill.proficiency,
                "order": skill.order,
                "star_count": len(starred_users),
                "is_starred": request.user.is_authenticated and any(
                    user.pk == request.user.pk for user in starred_users
                ),
                "starred_by_names": ", ".join(user.username for user in starred_users),
                "starred_by": [[user.username] for user in starred_users],
            },
        })

    return JsonResponse(data, safe=False)


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        with transaction.atomic():
            _record_activity(request.user, "delete", "experience", experience)
            experience.delete()
        messages.success(request, "Experience deleted successfully.")

    return redirect("main:show_experience")


@login_required(login_url="/login/")
def delete_skill(request, skill_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        with transaction.atomic():
            _record_activity(request.user, "delete", "skill", skill)
            skill.delete()
        messages.success(request, "Skill deleted successfully.")

    return redirect("main:show_skills")
