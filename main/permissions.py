from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """Tutorial Projects API policy; legacy HTML keeps change_project access."""

    message = 'Only the portfolio owner can change projects.'

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_superuser
            )
        )
