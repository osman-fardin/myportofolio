from rest_framework import serializers

from .models import Project


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

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            return False

        return request.user in obj.starred_by.all()
