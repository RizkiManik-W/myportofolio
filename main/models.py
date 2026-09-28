import uuid

from django.contrib.auth.models import User
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
    starred_by = models.ManyToManyField(User, blank=True, related_name="starred_skills")

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


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Created"),
        ("update", "Updated"),
        ("delete", "Deleted"),
    ]
    TARGET_CHOICES = [
        ("skill", "Skill"),
        ("experience", "Experience"),
    ]

    actor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="portfolio_activity_logs",
    )
    actor_username = models.CharField(max_length=150)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)
    target_id = models.CharField(max_length=64)
    target_title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "portfolio activity"
        verbose_name_plural = "portfolio activity"

    def __str__(self):
        return f"{self.actor_username} {self.get_action_display().lower()} {self.target_title}"
