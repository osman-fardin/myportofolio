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


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Experience Editors use the existing model permission, regardless of group name."""

    message = 'Only the portfolio owner can create/delete; Editors can update experiences.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return (
            request.method in ('PUT', 'PATCH')
            and request.user.has_perm('main.change_experience')
        )
