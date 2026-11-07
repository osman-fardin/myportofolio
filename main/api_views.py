from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Experience, Project
from .permissions import (
    IsPortfolioOwnerOrEditorOrReadOnly,
    IsPortfolioOwnerOrReadOnly,
)
from .querysets import with_star_summary
from .serializers import ExperienceSerializer, ProjectSerializer


@api_view(['GET', 'HEAD', 'POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    if request.method in ('GET', 'HEAD'):
        projects = with_star_summary(Project.objects.all(), request.user).order_by(
            'display_order', 'title', 'id',
        )
        title = request.query_params.get('title', '').strip()
        starred = request.query_params.get('starred', '').strip()

        if title:
            projects = projects.filter(title__icontains=title)

        if starred == 'mine':
            if request.user.is_authenticated:
                projects = projects.filter(_api_is_starred=True)
            else:
                projects = projects.none()

        serializer = ProjectSerializer(
            projects,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(
        data=request.data,
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'HEAD', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(
        with_star_summary(Project.objects.all(), request.user),
        pk=project_id,
    )

    if request.method in ('GET', 'HEAD'):
        serializer = ProjectSerializer(project, context={'request': request})
        return Response(serializer.data)

    if request.method == 'DELETE':
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project,
        data=request.data,
        partial=request.method == 'PATCH',
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)

    serializer = ProjectSerializer(project, context={'request': request})
    return Response(serializer.data)


@api_view(['GET', 'HEAD', 'POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    if request.method in ('GET', 'HEAD'):
        experiences = with_star_summary(Experience.objects.all(), request.user).order_by(
            '-started_at', 'id',
        )
        title = request.query_params.get('title', '').strip()
        category = request.query_params.get('category', '').strip()
        experience_status = request.query_params.get('status', '').strip()
        starred = request.query_params.get('starred', '').strip()

        if title:
            experiences = experiences.filter(title__icontains=title)
        if category:
            experiences = experiences.filter(category=category)
        if experience_status == 'ongoing':
            experiences = experiences.filter(ended_at__isnull=True)
        elif experience_status == 'completed':
            experiences = experiences.filter(ended_at__isnull=False)

        if starred == 'mine':
            if request.user.is_authenticated:
                experiences = experiences.filter(_api_is_starred=True)
            else:
                experiences = experiences.none()

        serializer = ExperienceSerializer(
            experiences, many=True, context={'request': request},
        )
        return Response(serializer.data)

    serializer = ExperienceSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'HEAD', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    experience = get_object_or_404(
        with_star_summary(Experience.objects.all(), request.user), pk=experience_id,
    )

    if request.method in ('GET', 'HEAD'):
        serializer = ExperienceSerializer(experience, context={'request': request})
        return Response(serializer.data)

    if request.method == 'DELETE':
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ExperienceSerializer(
        experience, data=request.data, partial=request.method == 'PATCH',
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)

    serializer = ExperienceSerializer(experience, context={'request': request})
    return Response(serializer.data)
