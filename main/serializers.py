from django.utils.html import strip_tags
from rest_framework import serializers

from .models import Project


def _clean_required_text(value):
    """API input bypasses ModelForm cleaning; output still needs escaping."""
    value = strip_tags(value).strip()

    if not value:
        raise serializers.ValidationError(
            'This field cannot be empty after removing HTML tags.',
            code='blank',
        )

    return value


class ProjectSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'project_type',
            'role',
            'description',
            'technologies',
            'thumbnail_path',
            'live_url',
            'source_url',
            'display_order',
            'star_count',
            'is_starred',
        ]
        read_only_fields = ['id']

    def validate_title(self, value):
        return _clean_required_text(value)

    def validate_project_type(self, value):
        return _clean_required_text(value)

    def validate_role(self, value):
        return _clean_required_text(value)

    def validate_description(self, value):
        return _clean_required_text(value)

    def validate_technologies(self, value):
        return _clean_required_text(value)

    def validate_thumbnail_path(self, value):
        return strip_tags(value).strip()

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            return False

        return request.user in obj.starred_by.all()
