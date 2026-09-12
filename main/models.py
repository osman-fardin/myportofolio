import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='full-time',
    )
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None

    @property
    def description_points(self):
        return [
            point.strip()
            for point in self.description.splitlines()
            if point.strip()
        ]


class Project(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(max_length=200)
    project_type = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    description = models.TextField()
    technologies = models.TextField()
    thumbnail_path = models.CharField(max_length=255, blank=True)
    live_url = models.URLField()
    source_url = models.URLField(blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'main:show_project_detail',
            kwargs={'project_id': self.id},
        )

    @property
    def technology_list(self):
        return [
            technology.strip()
            for technology in self.technologies.splitlines()
            if technology.strip()
        ]
