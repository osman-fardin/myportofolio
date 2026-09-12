from django.shortcuts import get_object_or_404, render

from .models import Experience, Project


def show_main(request):
    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'npm': '2506541723',
        'study_program': 'S1 Ilmu Komputer',
        'bio': (
            'CS student at Universitas Indonesia exploring the cloudy side '
            'of security, while helping guide new programmers through '
            'Programming Foundations 1. Equal parts builder, debugger, and '
            '“wait, let’s trace the code one more time” person.'
        ),
    }

    return render(request, 'index.html', context)


def show_experience(request):
    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'experience_list': Experience.objects.order_by('-started_at'),
    }

    return render(request, 'experience.html', context)


def show_projects(request):
    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'project_list': Project.objects.all(),
        'selected_project': None,
    }

    return render(request, 'projects.html', context)


def show_project_detail(request, project_id):
    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'project_list': Project.objects.all(),
        'selected_project': get_object_or_404(Project, id=project_id),
    }

    return render(request, 'projects.html', context)
