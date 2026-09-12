from django.contrib import admin

from .models import Experience, Project


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'started_at', 'ended_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')
    ordering = ('-started_at',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_type', 'role', 'display_order')
    list_editable = ('display_order',)
    search_fields = ('title', 'description', 'technologies')
    ordering = ('display_order', 'title')
