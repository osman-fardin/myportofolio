from django import forms

from .models import Experience, Project


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


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            'title',
            'description',
            'category',
            'thumbnail',
            'started_at',
            'ended_at',
        ]
        labels = {
            'title': 'Experience title',
            'description': 'Responsibilities and achievements',
            'category': 'Experience type',
            'thumbnail': 'Thumbnail URL',
            'started_at': 'Start date',
            'ended_at': 'End date',
        }
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': (
                        'Teaching Assistant, Programming Foundations 1'
                    ),
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'placeholder': (
                        'Write one responsibility or achievement per line'
                    ),
                    'rows': 5,
                }
            ),
            'category': forms.Select(),
            'thumbnail': forms.URLInput(
                attrs={
                    'placeholder': 'https://example.com/image.jpg',
                }
            ),
            'started_at': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    'type': 'datetime-local',
                },
            ),
            'ended_at': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    'type': 'datetime-local',
                },
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        started_at = cleaned_data.get('started_at')
        ended_at = cleaned_data.get('ended_at')

        if started_at and ended_at and ended_at < started_at:
            self.add_error(
                'ended_at',
                'End date cannot be earlier than start date.',
            )

        return cleaned_data
