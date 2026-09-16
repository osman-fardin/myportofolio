from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'project_type',
            'role',
            'description',
            'technologies',
            'thumbnail_path',
            'live_url',
            'source_url',
            'display_order',
        ]
        labels = {
            'title': 'Project title',
            'project_type': 'Project type',
            'role': 'My role',
            'description': 'Description',
            'technologies': 'Technologies',
            'thumbnail_path': 'Thumbnail path',
            'live_url': 'Live project URL',
            'source_url': 'Source code URL',
            'display_order': 'Display order',
        }
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder': 'Fasilkom Study Hub'}
            ),
            'project_type': forms.TextInput(
                attrs={'placeholder': 'Community Study Platform'}
            ),
            'role': forms.TextInput(
                attrs={'placeholder': 'Creator and Developer'}
            ),
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Describe the project and its purpose',
                    'rows': 4,
                }
            ),
            'technologies': forms.Textarea(
                attrs={
                    'placeholder': 'Write one technology per line',
                    'rows': 4,
                }
            ),
            'thumbnail_path': forms.TextInput(
                attrs={'placeholder': 'img/project-preview.jpg'}
            ),
            'live_url': forms.URLInput(
                attrs={'placeholder': 'https://example.com'}
            ),
            'source_url': forms.URLInput(
                attrs={'placeholder': 'https://github.com/username/project'}
            ),
            'display_order': forms.NumberInput(
                attrs={'min': 0}
            ),
        }
