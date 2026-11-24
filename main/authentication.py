from rest_framework.authentication import TokenAuthentication, get_authorization_header


class HeaderTokenAuthentication(TokenAuthentication):
    """Challenge invalid header tokens without changing legacy anonymous 403s.

    SessionAuthentication still enforces CSRF for cookie-authenticated writes.
    A supplied token takes priority, so an invalid token cannot fall back to a
    logged-in browser session and accidentally act as that session's user.
    """

    def authenticate_header(self, request):
        if get_authorization_header(request):
            return super().authenticate_header(request)
        return None
