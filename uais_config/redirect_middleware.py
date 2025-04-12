from django.shortcuts import redirect

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sprawdź, czy host to 1237.0.0.1
        if request.get_host() == '1237.0.0.1:8000':
            return redirect('login')  # Przekierowanie na login
        return self.get_response(request)