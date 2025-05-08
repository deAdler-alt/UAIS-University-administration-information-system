# management/views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, HttpResponseRedirect # Dodano HttpResponseRedirect
from django.db.models import Q

# Import modeli
from users.models import (
    User, LogEntry, RadaDyscypliny, SkladRD, Osoba, Funkcja_czlonka, Wydzial
)
# Import formularzy
# Dodano OsobaForm
from .forms import UserCreateForm, UserUpdateForm, SkladRDForm, OsobaForm

# --- Widoki dla User ---
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'management/user_list.html'
    context_object_name = 'users_list'
    paginate_by = 15
    def test_func(self): return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser
    def handle_no_permission(self): messages.error(self.request, "Nie masz uprawnień do przeglądania tej sekcji."); return redirect('home')
    def get_queryset(self):
        queryset = User.objects.all().select_related('wydzial', 'rada_dyscypliny_fk').order_by('email')
        search_query = self.request.GET.get('search_email', None)
        if search_query: queryset = queryset.filter(email__icontains=search_query)
        return queryset
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['current_search'] = self.request.GET.get('search_email', ''); return context

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'management/user_form.html'
    success_url = reverse_lazy('management:user_list')
    def test_func(self): return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser
    def handle_no_permission(self): messages.error(self.request, "Nie masz uprawnień do dodawania użytkowników."); return redirect('home')
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        messages.success(self.request, f"Użytkownik {email} został pomyślnie utworzony.")
        LogEntry.objects.create(user=self.request.user, action_type='USER_CREATED', details=f"Utworzono nowego użytkownika: {email}.", ip_address=self.request.META.get('REMOTE_ADDR'))
        response = super().form_valid(form)
        return response
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['title'] = 'Dodaj Nowego Użytkownika'; return context

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'management/user_form.html'
    success_url = reverse_lazy('management:user_list')
    def test_func(self): return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser
    def handle_no_permission(self): messages.error(self.request, "Nie masz uprawnień do edycji użytkowników."); return redirect('home')
    def form_valid(self, form):
        changed_fields_list = []
        if form.changed_data:
            for field_name in form.changed_data:
                if field_name not in ['password', 'password_confirm']:
                    old_value = form.initial.get(field_name, 'N/A')
                    new_value = form.cleaned_data.get(field_name, 'N/A')
                    if hasattr(old_value, '__str__'): old_value = str(old_value)
                    if hasattr(new_value, '__str__'): new_value = str(new_value)
                    changed_fields_list.append(f"Pole '{form.fields[field_name].label or field_name}': '{old_value}' -> '{new_value}'")
        changed_fields_str = "; ".join(changed_fields_list) if changed_fields_list else "Brak wykrytych zmian w danych."
        messages.success(self.request, f"Dane użytkownika {form.instance.email} zostały zaktualizowane.")
        LogEntry.objects.create(user=self.request.user, action_type='USER_UPDATED', details=f"Zaktualizowano dane użytkownika: {form.instance.email}. Zmiany: {changed_fields_str}", ip_address=self.request.META.get('REMOTE_ADDR'))
        response = super().form_valid(form)
        return response
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['title'] = f'Edytuj Użytkownika: {self.object.email}'; return context

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'management/user_confirm_delete.html'
    success_url = reverse_lazy('management:user_list')
    def test_func(self): return self.request.user.role == User.Role.ADMIN or self.request.user.is_superuser
    def handle_no_permission(self): messages.error(self.request, "Nie masz uprawnień do usuwania użytkowników."); return redirect('home')
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        user_email_to_delete = self.object.email
        LogEntry.objects.create(user=self.request.user, action_type='USER_DELETED', details=f"Usunięto użytkownika: {user_email_to_delete}.", ip_address=self.request.META.get('REMOTE_ADDR'))
        messages.success(self.request, f"Użytkownik {user_email_to_delete} został pomyślnie usunięty.")
        self.object.delete()
        return HttpResponseRedirect(success_url)
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['title'] = f'Potwierdź Usunięcie Użytkownika: {self.object.email}'; return context


# --- Widok dla Dziennika Zdarzeń ---
class LogEntryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LogEntry
    template_name = 'management/log_entry_list.html'
    context_object_name = 'log_entries'
    paginate_by = 20
    ordering = ['-timestamp']
    def test_func(self): return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser
    def handle_no_permission(self): messages.error(self.request, "Nie masz uprawnień do przeglądania dziennika zdarzeń."); return redirect('home')
    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        user_filter = self.request.GET.get('user_filter', None)
        action_type_filter = self.request.GET.get('action_type_filter', None)
        if user_filter: queryset = queryset.filter(Q(user__email__icontains=user_filter) | Q(user__first_name__icontains=user_filter) | Q(user__last_name__icontains=user_filter))
        if action_type_filter: queryset = queryset.filter(action_type=action_type_filter)
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dziennik Zdarzeń Systemowych'
        context['action_types'] = LogEntry.ACTION_TYPES
        context['current_user_filter'] = self.request.GET.get('user_filter', '')
        context['current_action_type_filter'] = self.request.GET.get('action_type_filter', '')
        return context

# --- Widok dla AJAX do ładowania Rad Dyscypliny ---
def load_rady_dyscypliny(request):
    wydzial_id = request.GET.get('wydzial_id')
    try:
        wydzial_id_int = int(wydzial_id)
        rady = RadaDyscypliny.objects.filter(wydzial_id=wydzial_id_int).order_by('nazwa')
        return JsonResponse(list(rady.values('id', 'nazwa')), safe=False)
    except (ValueError, TypeError): return JsonResponse([], safe=False)
    except Exception as e: print(f"Błąd w load_rady_dyscypliny: {e}"); return JsonResponse({'error': 'Błąd serwera'}, status=500)

# --- Widoki CRUD dla SkladRD ---
class SkladRDListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = SkladRD
    template_name = 'management/skladrd_list.html'
    context_object_name = 'sklad_list'
    paginate_by = 25
    def test_func(self): return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser
    def handle_no_permission(self): messages.error(self.request, "Nie masz uprawnień do zarządzania składami rad."); return redirect('home')
    def get_queryset(self):
        queryset = SkladRD.objects.select_related('rd', 'osoba', 'funkcja_czlonka', 'rd__wydzial').order_by('rd__wydzial__nazwa', 'rd__nazwa', 'osoba__nazwisko', 'osoba__imie')
        rada_filter_id = self.request.GET.get('rada_filter', None)
        if rada_filter_id:
            try: queryset = queryset.filter(rd_id=int(rada_filter_id))
            except ValueError: pass
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Zarządzanie Składami Rad Dyscyplin'
        context['rady_dyscyplin'] = RadaDyscypliny.objects.select_related('wydzial').order_by('wydzial__nazwa', 'nazwa')
        context['current_rada_filter'] = self.request.GET.get('rada_filter', '')
        return context

class SkladRDCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = SkladRD
    form_class = SkladRDForm
    template_name = 'management/skladrd_form.html'
    success_url = reverse_lazy('management:skladrd_list')
    def test_func(self): return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser
    def handle_no_permission(self): messages.error(self.request, "Nie masz uprawnień do dodawania członków do składów rad."); return redirect('management:skladrd_list')
    def form_valid(self, form):
        response = super().form_valid(form)
        # TODO: Logowanie zdarzenia do LogEntry (potrzebne nowe typy akcji)
        # LogEntry.objects.create(user=self.request.user, action_type='SKLAD_RD_MEMBER_ADDED', details=f"Dodano członka: {self.object.osoba} (Funkcja: {self.object.funkcja_czlonka}) do składu: {self.object.rd}.", ip_address=self.request.META.get('REMOTE_ADDR'))
        messages.success(self.request, f"Dodano {self.object.osoba} do składu {self.object.rd}.")
        return response
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['title'] = 'Dodaj Członka do Składu Rady Dyscypliny'; return context

class SkladRDUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SkladRD
    form_class = SkladRDForm
    template_name = 'management/skladrd_form.html'
    success_url = reverse_lazy('management:skladrd_list')
    def test_func(self): return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser
    def handle_no_permission(self): messages.error(self.request, "Nie masz uprawnień do edycji członków składów rad."); return redirect('management:skladrd_list')
    def form_valid(self, form):
        # TODO: Logowanie zdarzenia do LogEntry (potrzebne nowe typy akcji + logika zmian)
        messages.success(self.request, f"Zaktualizowano dane członkostwa dla {form.instance.osoba} w {form.instance.rd}.")
        return super().form_valid(form)
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['title'] = f'Edytuj Członkostwo: {self.object.osoba} ({self.object.rd})'; return context

class SkladRDDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = SkladRD
    template_name = 'management/skladrd_confirm_delete.html'
    success_url = reverse_lazy('management:skladrd_list')
    def test_func(self): return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser
    def handle_no_permission(self): messages.error(self.request, "Nie masz uprawnień do usuwania członków ze składów rad."); return redirect('management:skladrd_list')
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        osoba = self.object.osoba
        rd = self.object.rd
        # TODO: Logowanie zdarzenia do LogEntry (potrzebne nowe typy akcji)
        messages.success(self.request, f"Usunięto {osoba} ze składu {rd}.")
        self.object.delete()
        return HttpResponseRedirect(success_url)
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['title'] = f'Potwierdź Usunięcie Członkostwa: {self.object.osoba} ({self.object.rd})'; return context


# --- NOWE Widoki CRUD dla Osoba ---

class OsobaListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Osoba
    template_name = 'management/osoba_list.html' # Nowy szablon
    context_object_name = 'osoby_list'
    paginate_by = 15 # Możesz dostosować

    def test_func(self):
        # Dostęp dla Admina i Obsługi (dostosuj wg potrzeb)
        return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do zarządzania osobami.")
        return redirect('home')

    def get_queryset(self):
        queryset = Osoba.objects.all().order_by('nazwisko', 'imie')
        # Wyszukiwanie
        search_query = self.request.GET.get('search_person', None)
        if search_query:
            queryset = queryset.filter(
                Q(imie__icontains=search_query) |
                Q(nazwisko__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Zarządzanie Osobami'
        context['current_search'] = self.request.GET.get('search_person', '') # Do wyświetlenia w polu wyszukiwania
        return context

class OsobaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Osoba
    form_class = OsobaForm
    template_name = 'management/osoba_form.html' # Nowy szablon
    success_url = reverse_lazy('management:osoba_list') # Po sukcesie wracamy do listy osób

    def test_func(self):
        # Uprawnienia np. tylko dla ADMIN/OBSLUGA
        return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do dodawania osób.")
        return redirect('management:osoba_list') # Wracamy do listy osób

    def form_valid(self, form):
        # Zapisujemy obiekt przed logowaniem, aby mieć do niego dostęp w komunikacie
        response = super().form_valid(form)
        # TODO: Logowanie zdarzenia do LogEntry (nowy typ akcji OSOBA_CREATED?)
        messages.success(self.request, f"Dodano nową osobę: {self.object}.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj Nową Osobę'
        return context

class OsobaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Osoba
    form_class = OsobaForm
    template_name = 'management/osoba_form.html' # Ten sam szablon co dla tworzenia
    success_url = reverse_lazy('management:osoba_list')

    def test_func(self):
        # Uprawnienia np. tylko dla ADMIN/OBSLUGA
        return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do edycji osób.")
        return redirect('management:osoba_list')

    def form_valid(self, form):
        # TODO: Logowanie zdarzenia do LogEntry (nowy typ akcji OSOBA_UPDATED? + logika zmian)
        messages.success(self.request, f"Zaktualizowano dane osoby: {self.object}.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edytuj Osobę: {self.object}'
        # Tutaj w przyszłości można dodać logikę dla inline formsetów do zarządzania adresami
        return context

class OsobaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Osoba
    template_name = 'management/osoba_confirm_delete.html' # Nowy szablon
    success_url = reverse_lazy('management:osoba_list')

    def test_func(self):
         # Uprawnienia np. tylko dla ADMIN/OBSLUGA
        return self.request.user.role in [User.Role.ADMIN, User.Role.OBSLUGA] or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do usuwania osób.")
        return redirect('management:osoba_list')

    # Używamy metody delete dla logowania przed usunięciem
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        osoba_str = str(self.object) # Pobierz reprezentację obiektu przed usunięciem
        # TODO: Logowanie zdarzenia do LogEntry (nowy typ akcji OSOBA_DELETED?)
        messages.success(self.request, f"Usunięto osobę: {osoba_str}.")
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Potwierdź Usunięcie Osoby: {self.object}'
        return context