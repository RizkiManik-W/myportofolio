import uuid

from django.db import models


class Skill(models.Model):
    SKILL_TYPES = [
        ("programming", "Programming Languages"),
        ("web", "Web Development"),
        ("game", "Game Development"),
        ("database", "Database"),
        ("systems", "Systems & Networking"),
        ("tools", "Tools & Technologies"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=SKILL_TYPES,
        default="programming",
    )
    proficiency = models.CharField(max_length=255, blank=True, default="")
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ("internship", "Internship"),
        ("research", "Research"),
        ("volunteer", "Volunteer"),
        ("part-time", "Part-Time"),
        ("full-time", "Full-Time"),
        ("freelance", "Freelance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default="full-time",
    )
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None