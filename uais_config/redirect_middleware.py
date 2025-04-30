from django.shortcuts import redirect

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sprawdź, czy host to 127.0.0.1:8000, ścieżka to "/" i użytkownik jest niezalogowany
        if request.get_host() == '127.0.0.1:8000' and request.path == '/' and not request.user.is_authenticated:
            return redirect('/accounts/login')  # Przekierowanie na login
        return self.get_response(request)