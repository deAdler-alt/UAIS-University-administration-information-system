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
        return redirect('home') # Przekieruj na stronę główną
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
        # Takie samo zachowanie przy braku uprawnień
        messages.error(self.request, "Nie masz uprawnień do dodawania użytkowników.")
        return redirect('home')

    def form_valid(self, form):
        # Dodajemy komunikat o sukcesie
        messages.success(self.request, f"Użytkownik {form.cleaned_data.get('email')} został pomyślnie utworzony.")
        return super().form_valid(form)

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
        return redirect('home')

    def form_valid(self, form):
        # Komunikat o sukcesie
        messages.success(self.request, f"Dane użytkownika {form.instance.email} zostały zaktualizowane.")
        return super().form_valid(form)

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
        return redirect('home')

    def get_context_data(self, **kwargs):
        # Ustawiamy tytuł dla szablonu
        context = super().get_context_data(**kwargs)
        context['title'] = f'Potwierdź Usunięcie Użytkownika: {self.object.email}'
        return context