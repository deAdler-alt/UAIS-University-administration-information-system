# management/views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse # Zmieniono HttpResponseRedirect na JsonResponse dla AJAX
from django.db.models import Q # Do wyszukiwania

# Import modeli
from users.models import User, LogEntry, RadaDyscypliny # Dodano import LogEntry i RadaDyscypliny
# Import formularzy
from .forms import UserCreateForm, UserUpdateForm

# --- Widok listy użytkowników ---
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'management/user_list.html'
    context_object_name = 'users_list'
    paginate_by = 15

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do przeglądania tej sekcji.")
        return redirect('home') # Usunięto response.status_code = 403, redirect to załatwia

    def get_queryset(self):
        queryset = User.objects.all().order_by('email')
        search_query = self.request.GET.get('search_email', None) # Zmieniono parametr na search_email dla jasności
        if search_query:
            queryset = queryset.filter(email__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search_email', '') # Do wyświetlenia w polu wyszukiwania
        return context

# --- Widok tworzenia użytkownika ---
class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'management/user_form.html'
    success_url = reverse_lazy('management:user_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do dodawania użytkowników.")
        return redirect('home')

    def form_valid(self, form):
        messages.success(self.request, f"Użytkownik {form.cleaned_data.get('email')} został pomyślnie utworzony.")
        # Logowanie zdarzenia
        LogEntry.objects.create(
            user=self.request.user,
            action_type='USER_CREATED',
            details=f"Utworzono nowego użytkownika: {form.cleaned_data.get('email')}.",
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        response = super().form_valid(form)
        # response.status_code = 201 # CreateView domyślnie zwraca 302 po sukcesie, status code nie jest tu potrzebny
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj Nowego Użytkownika'
        return context

# --- Widok aktualizacji użytkownika ---
class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'management/user_form.html'
    success_url = reverse_lazy('management:user_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do edycji użytkowników.")
        return redirect('home')

    def form_valid(self, form):
        # Zbieranie informacji o zmienionych polach dla logu
        changed_fields_list = []
        if form.changed_data:
            for field_name in form.changed_data:
                # Unikamy logowania hasła
                if field_name not in ['password', 'password_confirm']:
                    old_value = form.initial.get(field_name, 'N/A')
                    new_value = form.cleaned_data.get(field_name, 'N/A')
                    # Dla pól ForeignKey, wyświetlajmy czytelne nazwy
                    if hasattr(old_value, '__str__'): old_value = str(old_value)
                    if hasattr(new_value, '__str__'): new_value = str(new_value)
                    changed_fields_list.append(f"Pole '{form.fields[field_name].label or field_name}': '{old_value}' -> '{new_value}'")
        
        changed_fields_str = "; ".join(changed_fields_list) if changed_fields_list else "Brak wykrytych zmian w danych."

        messages.success(self.request, f"Dane użytkownika {form.instance.email} zostały zaktualizowane.")
        # Logowanie zdarzenia
        LogEntry.objects.create(
            user=self.request.user,
            action_type='USER_UPDATED',
            details=f"Zaktualizowano dane użytkownika: {form.instance.email}. Zmiany: {changed_fields_str}",
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        response = super().form_valid(form)
        # response.status_code = 200 # UpdateView domyślnie zwraca 302 po sukcesie
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edytuj Użytkownika: {self.object.email}'
        return context

# --- Widok usuwania użytkownika ---
class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'management/user_confirm_delete.html'
    success_url = reverse_lazy('management:user_list')
    # success_message = "Użytkownik został pomyślnie usunięty." # Można ustawić, ale log będzie bardziej szczegółowy

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do usuwania użytkowników.")
        return redirect('home')

    def form_valid(self, form): # DeleteView używa form_valid, ale także delete()
        user_email_to_delete = self.object.email # Pobierz email przed usunięciem obiektu
        LogEntry.objects.create(
            user=self.request.user,
            action_type='USER_DELETED',
            details=f"Usunięto użytkownika: {user_email_to_delete}.",
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        messages.success(self.request, f"Użytkownik {user_email_to_delete} został pomyślnie usunięty.")
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Potwierdź Usunięcie Użytkownika: {self.object.email}'
        return context

# --- NOWY Widok dla Dziennika Zdarzeń ---
class LogEntryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LogEntry
    template_name = 'management/log_entry_list.html' # Nowy szablon
    context_object_name = 'log_entries'
    paginate_by = 20 # Możesz dostosować
    ordering = ['-timestamp'] # Najnowsze na górze

    def test_func(self):
        # Dostęp dla Admina i Obsługi
        return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do przeglądania dziennika zdarzeń.")
        return redirect('home')

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrowanie (opcjonalne, można rozbudować)
        user_filter = self.request.GET.get('user_filter', None)
        action_type_filter = self.request.GET.get('action_type_filter', None)

        if user_filter:
            queryset = queryset.filter(Q(user__email__icontains=user_filter) | Q(user__first_name__icontains=user_filter) | Q(user__last_name__icontains=user_filter))
        if action_type_filter:
            queryset = queryset.filter(action_type=action_type_filter)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dziennik Zdarzeń Systemowych'
        context['action_types'] = LogEntry.ACTION_TYPES # Do filtrowania w szablonie
        context['current_user_filter'] = self.request.GET.get('user_filter', '')
        context['current_action_type_filter'] = self.request.GET.get('action_type_filter', '')
        return context

# --- NOWY Widok dla AJAX do ładowania Rad Dyscypliny ---
def load_rady_dyscypliny(request):
    wydzial_id = request.GET.get('wydzial_id')
    try:
        # Upewniamy się, że wydzial_id jest liczbą całkowitą
        wydzial_id_int = int(wydzial_id)
        rady = RadaDyscypliny.objects.filter(wydzial_id=wydzial_id_int).order_by('nazwa')
        # Zwracamy listę słowników, każdy słownik ma 'id' i 'nazwa'
        return JsonResponse(list(rady.values('id', 'nazwa')), safe=False)
    except (ValueError, TypeError):
        # Jeśli wydzial_id nie jest liczbą lub jest None
        return JsonResponse([], safe=False)
    except Exception as e:
        # Logowanie błędu serwera, jeśli coś innego pójdzie nie tak
        print(f"Błąd w load_rady_dyscypliny: {e}") # Loguj do konsoli/pliku
        return JsonResponse({'error': 'Błąd serwera'}, status=500)