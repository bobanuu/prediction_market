from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication that doesn't enforce CSRF checks.
    This is needed for API endpoints that are accessed from the frontend.
    """
    
    def enforce_csrf(self, request):
        """
        Don't enforce CSRF checks for API endpoints.
        """
        return
