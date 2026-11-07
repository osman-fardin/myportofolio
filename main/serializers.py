from django.utils.html import strip_tags
from rest_framework import serializers

from .models import Experience, Project


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


class ExperienceSerializer(serializers.ModelSerializer):
    description_points = serializers.ListField(
        child=serializers.CharField(), read_only=True,
    )
    category_label = serializers.CharField(
        source='get_category_display', read_only=True,
    )
    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            'id',
            'title',
            'description',
            'description_points',
            'category',
            'category_label',
            'thumbnail',
            'started_at',
            'ended_at',
            'is_ongoing',
            'star_count',
            'is_starred',
        ]
        read_only_fields = ['id']

    def validate_title(self, value):
        return _clean_required_text(value)

    def validate_description(self, value):
        return _clean_required_text(value)

    def validate(self, attrs):
        if self.instance is None and 'started_at' not in attrs:
            # Use one model default for both validation and the eventual save.
            attrs['started_at'] = (
                Experience._meta.get_field('started_at').get_default()
            )

        started_at = attrs.get(
            'started_at', self.instance.started_at if self.instance else None,
        )
        ended_at = attrs.get(
            'ended_at', self.instance.ended_at if self.instance else None,
        )

        # PATCH must compare submitted dates with any dates kept on the instance.
        if ended_at is not None and ended_at < started_at:
            raise serializers.ValidationError({
                'ended_at': 'End date cannot be earlier than start date.',
            })

        return attrs

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            return False

        return request.user in obj.starred_by.all()
