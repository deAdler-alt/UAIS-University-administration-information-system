# management/views.py
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.models import User # Importujemy model User z aplikacji users

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'management/user_list.html' # Ścieżka do szablonu
    context_object_name = 'users_list' # Nazwa listy użytkowników w szablonie
    paginate_by = 15 # Ile użytkowników na stronę

    def test_func(self):
        # Sprawdza, czy użytkownik ma dostęp do tego widoku
        # Dostęp ma tylko ADMIN lub superuser
        return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser

    def handle_no_permission(self):
        # Co zrobić, jeśli użytkownik nie ma uprawnień
        # Można przekierować na stronę główną lub pokazać błąd 403
        # from django.http import HttpResponseForbidden
        # return HttpResponseForbidden("Nie masz uprawnień do przeglądania tej strony.")
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, "Nie masz uprawnień do dostępu do tej sekcji.")
        return redirect('home') # Przekieruj na stronę główną

    def get_queryset(self):
        # Możemy sortować użytkowników, np. po emailu
        return User.objects.all().order_by('email')