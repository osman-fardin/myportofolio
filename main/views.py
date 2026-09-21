import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ExperienceForm, ProjectForm
from .models import Experience, Project


def show_main(request):
    last_login = (
        request.COOKIES.get('last_login')
        or 'No login session recorded'
    )

    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'npm': '2506541723',
        'study_program': 'S1 Ilmu Komputer',
        'last_login': last_login,
        'bio': (
            'CS student at Universitas Indonesia exploring the cloudy side '
            'of security, while helping guide new programmers through '
            'Programming Foundations 1. Equal parts builder, debugger, and '
            '“wait, let’s trace the code one more time” person.'
        ),
    }

    return render(request, 'index.html', context)


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            'Account created successfully. Please log in.',
        )
        return redirect('main:login')

    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'form': form,
    }

    return render(request, 'register.html', context)


def login_user(request):
    form = AuthenticationForm(
        request,
        data=request.POST or None,
    )

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        response = redirect('main:show_main')
        response.set_cookie(
            'last_login',
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )

        return response

    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'form': form,
    }

    return render(request, 'login.html', context)


def logout_user(request):
    logout(request)

    response = redirect('main:show_main')
    response.delete_cookie('last_login')

    return response


def _get_filtered_experiences(request):
    experiences = Experience.objects.order_by('-started_at')

    title_query = request.GET.get('title', '').strip()
    category_filter = request.GET.get('category', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if title_query:
        experiences = experiences.filter(
            title__icontains=title_query,
        )

    if category_filter:
        experiences = experiences.filter(
            category=category_filter,
        )

    if status_filter == 'ongoing':
        experiences = experiences.filter(
            ended_at__isnull=True,
        )
    elif status_filter == 'completed':
        experiences = experiences.filter(
            ended_at__isnull=False,
        )

    return experiences


def show_experience(request):
    json_response = get_experiences_json(request)

    experiences = serializers.deserialize(
        'json',
        json_response.content.decode('utf-8'),
    )
    experiences = [
        experience.object
        for experience in experiences
    ]

    title_query = request.GET.get('title', '').strip()
    category_filter = request.GET.get('category', '').strip()
    status_filter = request.GET.get('status', '').strip()

    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'experience_list': experiences,
        'category_choices': Experience.EXPERIENCE_CHOICES,
        'title_query': title_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'has_active_filters': bool(
            title_query
            or category_filter
            or status_filter
        ),
    }

    return render(request, 'experience.html', context)


def get_experiences_json(request):
    experiences = _get_filtered_experiences(request)

    experiences_json = serializers.serialize(
        'json',
        experiences,
    )

    return HttpResponse(
        experiences_json,
        content_type='application/json',
    )


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


def update_experience(request, experience_id):
    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )

    if request.method == 'POST':
        form = ExperienceForm(
            request.POST,
            instance=experience,
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Experience updated successfully.',
            )
            return redirect('main:show_experience')
    else:
        form = ExperienceForm(instance=experience)

    context = {
        'name': 'Muhammad Osman Fardin',
        'display_name': 'Muhammad Osman Fardin',
        'form': form,
        'form_kicker': 'Update experience',
        'form_title': 'Edit experience',
        'form_description': (
            'Refine the role, timeline, or achievements '
            'shown in this experience.'
        ),
        'submit_label': 'Save changes',
    }

    return render(request, 'experience_form.html', context)


@require_POST
def delete_experience(request, experience_id):
    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )
    experience.delete()

    messages.success(
        request,
        'Experience deleted successfully.',
    )

    return redirect('main:show_experience')


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


@login_required(login_url='/login/')
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url='/login/')
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url='/login/')
@require_POST
def toggle_project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)

    return redirect('main:show_project_detail', project_id=project.id)
