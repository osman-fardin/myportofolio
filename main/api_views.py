from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from .models import Project
from .permissions import IsPortfolioOwnerOrReadOnly
from .serializers import ProjectSerializer


@api_view(['GET', 'HEAD', 'POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    if request.method in ('GET', 'HEAD'):
        projects = Project.objects.prefetch_related('starred_by').order_by(
            'display_order', 'title', 'id',
        )
        title = request.query_params.get('title', '').strip()
        starred = request.query_params.get('starred', '').strip()

        if title:
            projects = projects.filter(title__icontains=title)

        if starred == 'mine':
            if request.user.is_authenticated:
                projects = projects.filter(starred_by=request.user)
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
