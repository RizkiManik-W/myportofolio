from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Project, Skill
from main.serializers import ProjectSerializer, SkillSerializer
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly
from main.views import _record_activity




@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("starred_by").order_by("title", "id")
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    with transaction.atomic():
        project = serializer.save()
        _record_activity(request.user, "create", "project", project)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related("starred_by"), pk=project_id,
    )

    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        with transaction.atomic():
            _record_activity(request.user, "delete", "project", project)
            project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    with transaction.atomic():
        project = serializer.save()
        _record_activity(request.user, "update", "project", project)
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    with transaction.atomic():
        project = get_object_or_404(
            Project.objects.select_for_update(), pk=project_id,
        )
        if project.starred_by.filter(pk=request.user.pk).exists():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)

@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def skill_list(request):
    if request.method in ("GET", "HEAD"):
        skills = Skill.objects.prefetch_related("starred_by").order_by(
            "order", "title", "id",
        )
        title = request.query_params.get("title", "").strip()
        if title:
            skills = skills.filter(title__icontains=title)

        serializer = SkillSerializer(
            skills, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = SkillSerializer(
        data=request.data, context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    with transaction.atomic():
        skill = serializer.save()
        _record_activity(request.user, "create", "skill", skill)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def skill_detail(request, skill_id):
    skill = get_object_or_404(
        Skill.objects.prefetch_related("starred_by"), pk=skill_id,
    )

    if request.method in ("GET", "HEAD"):
        serializer = SkillSerializer(skill, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        with transaction.atomic():
            _record_activity(request.user, "delete", "skill", skill)
            skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = SkillSerializer(
        skill,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    with transaction.atomic():
        skill = serializer.save()
        _record_activity(request.user, "update", "skill", skill)

    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def skill_star(request, skill_id):
    with transaction.atomic():
        skill = get_object_or_404(
            Skill.objects.select_for_update(), pk=skill_id,
        )
        if skill.starred_by.filter(pk=request.user.pk).exists():
            skill.starred_by.remove(request.user)
        else:
            skill.starred_by.add(request.user)

    serializer = SkillSerializer(skill, context={"request": request})
    return Response(serializer.data)