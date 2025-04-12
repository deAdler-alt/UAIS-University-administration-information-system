# management/views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from users.models import User
from .forms import UserCreateForm
from django.views.generic import ListView, CreateView, UpdateView # Dodajemy UpdateView
from .forms import UserCreateForm, UserUpdateForm # Importujemy oba formularze
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'management/user_list.html'
    context_object_name = 'users_list'
    paginate_by = 15

    def test_func(self):
        # Sprawdza, czy użytkownik ma dostęp do tego widoku
        return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser

    # --- DODANA METODA ---
    def handle_no_permission(self):
        # Co zrobić, jeśli użytkownik nie ma uprawnień do widoku listy
        messages.error(self.request, "Nie masz uprawnień do przeglądania tej sekcji.")
        response = redirect('home') # Przekierowujemy na stronę główną
        response.status_code = 403  # Kod błędu 403 (Forbidden)
        return response
    # --- KONIEC DODANEJ METODY ---

    def get_queryset(self):
        # Pobieramy i sortujemy użytkowników
        return User.objects.all().order_by('email')

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'management/user_form.html'
    success_url = reverse_lazy('management:user_list')

    def test_func(self):
        # Takie same uprawnienia jak dla listy
        return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do dodawania użytkowników.")
        response = redirect('home')
        response.status_code = 403  # Ustawiamy kod błędu 403
        return response

    # z wykorzystaniem postmana można dodać użytkownika jako wartości pustę
    # trzeba dodać walidację, ale nie teraz
    def form_valid(self, form):
        # Dodajemy komunikat o sukcesie
        messages.success(self.request, f"Użytkownik {form.cleaned_data.get('email')} został pomyślnie utworzony.")
        response = super().form_valid(form)
        response.status_code = 201  # Ustawiamy kod odpowiedzi na 201 (Created)
        return response

    def get_context_data(self, **kwargs):
        # Dodajemy tytuł do kontekstu szablonu
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj Nowego Użytkownika'
        return context
    
class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm # Używamy formularza edycji
    template_name = 'management/user_form.html' # Ten sam szablon co dla tworzenia
    success_url = reverse_lazy('management:user_list') # Po edycji wracamy na listę

    def test_func(self):
        # Uprawnienia - ADMIN lub superuser
        return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do edycji użytkowników.")
        response = redirect('home')
        response.status_code = 403  # Kod błędu 403 (Forbidden)
        return response

    def form_valid(self, form):
        messages.success(self.request, f"Dane użytkownika {form.instance.email} zostały zaktualizowane.")
        response = super().form_valid(form)
        response.status_code = 200  # Kod odpowiedzi 200 (OK)
        return response

    def get_context_data(self, **kwargs):
        # Ustawiamy tytuł dla szablonu
        context = super().get_context_data(**kwargs)
        # 'object' to standardowa nazwa obiektu edytowanego w UpdateView
        context['title'] = f'Edytuj Użytkownika: {self.object.email}'
        return context

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'management/user_confirm_delete.html'
    success_url = reverse_lazy('management:user_list')
    success_message = "Użytkownik został pomyślnie usunięty."

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do usuwania użytkowników.")
        response = redirect('home')
        response.status_code = 403  # Kod błędu 403 (Forbidden)
        return response

    def get_context_data(self, **kwargs):
        # Ustawiamy tytuł dla szablonu
        context = super().get_context_data(**kwargs)
        context['title'] = f'Potwierdź Usunięcie Użytkownika: {self.object.email}'
        return context