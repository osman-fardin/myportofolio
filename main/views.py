from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ExperienceForm, ProjectForm
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


def create_experience(request):
    if request.method == 'POST':
        form = ExperienceForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Experience added successfully.',
            )
            return redirect('main:show_experience')
    else:
        form = ExperienceForm()

    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'form': form,
        'form_kicker': 'New experience',
        'form_title': 'Add experience',
        'form_description': (
            'Add a role, contribution, or learning experience '
            'to the portfolio.'
        ),
        'submit_label': 'Add experience',
    }

    return render(request, 'experience_form.html', context)


def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        'json',
        json_response.content.decode('utf-8'),
    )
    projects = [project.object for project in projects]

    title_query = request.GET.get('title', '').strip()

    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'project_list': projects,
        'selected_project': None,
        'title_query': title_query,
    }

    return render(request, 'projects.html', context)


def get_projects_json(request):
    title_query = request.GET.get('title', '').strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize('json', projects)

    return HttpResponse(
        projects_json,
        content_type='application/json',
    )


def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Project added successfully.')
            return redirect('main:show_projects')
    else:
        form = ProjectForm()

    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'form': form,
    }

    return render(request, 'projects_form.html', context)


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('main:show_projects')

    return redirect('main:show_projects')


def show_project_detail(request, project_id):
    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'project_list': Project.objects.all(),
        'selected_project': get_object_or_404(Project, id=project_id),
    }

    return render(request, 'projects.html', context)
