# users/views.py

from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm 
import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage # Dodajemy EmailMessage dla szablonów
from django.template.loader import render_to_string # Do renderowania szablonu email
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login as auth_login, get_user_model # Zmieniamy nazwę importu login
from django.conf import settings
from django.contrib import messages
from .forms import PinVerificationForm # Importujemy nowy formularz PIN
from . import views

User = get_user_model()


# Poprawiona funkcja home_view
# @login_required # Jeśli chcesz, aby była tylko dla zalogowanych
def home_view(request):
    dummy_commits = [
         {
             'sha': 'a1b2c3d4',
             'author': 'Jan Kowalski',
             'date': '2025-04-07T10:30:00Z',
             'message': 'Fix: Poprawiono błąd walidacji w formularzu 217.'
         },
         {
             'sha': 'e5f6g7h8',
             'author': 'Anna Nowak',
             'date': '2025-04-07T09:15:00Z',
             'message': 'Feat: Dodano nową funkcję eksportu do PDF.\n\n- Umożliwia eksport danych z tabeli Y.\n- Dodano testy jednostkowe.'
         },
         {
             'sha': 'i9j0k1l2',
             'author': 'Jan Kowalski',
             'date': '2025-04-06T18:00:00Z',
             'message': 'Refactor: Zmieniono strukturę modułu Z.'
         },
         {
             'sha': 'm3n4o5p6',
             'author': 'Piotr Wiśniewski',
             'date': '2025-04-06T15:45:00Z',
             'message': 'Style: Poprawki w wyglądzie strony logowania.'
         },
     ]

    # --- POCZĄTEK BRAKUJĄCEGO KODU ---
    context = {
        'welcome_message': 'Witaj w systemie UAIS!', # Możesz usunąć, jeśli nie używasz
        'commits': dummy_commits # Przekazujemy commity do szablonu
    }
    # Zwracamy wyrenderowany szablon jako odpowiedź HTTP
    return render(request, 'home.html', context)
    # --- KONIEC BRAKUJĄCEGO KODU ---


# Funkcja login_choice_view (wygląda OK)
# users/views.py

#Logika views

def login_choice_view(request):
    # Jeśli użytkownik jest już zalogowany, przekieruj go na stronę główną
    if request.user.is_authenticated:
        return redirect('home')

    # Tworzymy instancję formularza logowania, aby przekazać ją do szablonu
    form = AuthenticationForm()
    context = {
        'form': form, # Przekazujemy pusty formularz do szablonu
        'title': 'Wybierz Metodę Logowania'
    }
    return render(request, 'users/login_choice.html', context)

def process_local_login_view(request):
    if request.user.is_authenticated:
         return redirect('home') # Już zalogowany, idź do domu

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Hasło poprawne - Inicjujemy proces 2FA
            try:
                pin = str(random.randint(1000, 9999)).zfill(4) # Losowy PIN 4 cyfry, z wiodącymi zerami
                pin_expiry = timezone.now() + timedelta(minutes=10) # Ważność 10 minut
                pin_hash = make_password(pin) # Hashujemy PIN

                # Zapisujemy w sesji
                request.session['2fa_user_pk'] = user.pk
                request.session['2fa_pin_hash'] = pin_hash
                request.session['2fa_expiry'] = pin_expiry.isoformat()
                request.session['2fa_email'] = user.email # Zapiszmy też email dla wygody

                # Przygotuj i wyślij email z PINem używając szablonu
                email_context = {'pin': pin, 'user': user}
                subject = 'Twój kod weryfikacyjny UAIS'
                body = render_to_string('users/emails/2fa_pin_email.txt', email_context)

                # Używamy EmailMessage dla łatwiejszego zarządzania
                email_message = EmailMessage(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL, # Od
                    [user.email], # Do
                )
                email_message.send(fail_silently=False) # Wyślij (do konsoli)

                messages.info(request, f'Na adres {user.email} wysłano kod weryfikacyjny PIN.')
                return redirect('pin_verification') # Przekierowanie do strony weryfikacji PIN

            except Exception as e:
                # Obsługa błędu generowania/wysyłki emaila
                messages.error(request, f'Wystąpił błąd podczas inicjowania weryfikacji 2FA. Spróbuj ponownie. Błąd: {e}')
                # Renderujemy stronę wyboru z oryginalnym formularzem logowania (bez błędów, bo hasło było dobre)
                login_form = AuthenticationForm()
                context = {'form': login_form, 'title': 'Wybierz Metodę Logowania'}
                return render(request, 'users/login_choice.html', context)
        else:
            # Formularz logowania niepoprawny (złe hasło/email)
            messages.error(request, "Niepoprawny email lub hasło.") # Dodajmy własny komunikat
            context = {'form': form, 'title': 'Wybierz Metodę Logowania'} # Przekazujemy formularz Z BŁĘDAMI
            return render(request, 'users/login_choice.html', context)
    else:
        # Metoda GET nie powinna tu trafiać bezpośrednio
        return redirect('login')

# users/views.py
# ...

def pin_verification_view(request):
    user_pk = request.session.get('2fa_user_pk')
    pin_hash = request.session.get('2fa_pin_hash')
    expiry_str = request.session.get('2fa_expiry')
    user_email = request.session.get('2fa_email', 'Twój adres email') # Pobieramy email z sesji

    # Sprawdź, czy dane 2FA są w sesji
    if not all([user_pk, pin_hash, expiry_str]):
        messages.error(request, 'Sesja weryfikacji wygasła lub jest nieprawidłowa. Zaloguj się ponownie.')
        return redirect('login')

    try:
        expiry = timezone.datetime.fromisoformat(expiry_str)
    except ValueError:
         messages.error(request, 'Błąd sesji weryfikacji. Zaloguj się ponownie.')
         return redirect('login')


    # Sprawdź ważność PINu
    if timezone.now() > expiry:
        # Usuń stare dane z sesji
        request.session.pop('2fa_user_pk', None)
        request.session.pop('2fa_pin_hash', None)
        request.session.pop('2fa_expiry', None)
        request.session.pop('2fa_email', None)
        messages.error(request, 'Kod PIN wygasł. Zaloguj się ponownie, aby otrzymać nowy kod.')
        return redirect('login')

    if request.method == 'POST':
        form = PinVerificationForm(request.POST)
        if form.is_valid():
            entered_pin = form.cleaned_data['pin']
            # Sprawdź hash PINu
            if check_password(entered_pin, pin_hash):
                try:
                    user = User.objects.get(pk=user_pk)
                    # PIN poprawny - zaloguj użytkownika
                    auth_login(request, user) # Używamy zaimportowanego 'auth_login'
                    # Usuń dane 2FA z sesji
                    request.session.pop('2fa_user_pk', None)
                    request.session.pop('2fa_pin_hash', None)
                    request.session.pop('2fa_expiry', None)
                    request.session.pop('2fa_email', None)
                    messages.success(request, 'Zostałeś pomyślnie zalogowany.')
                    return redirect(settings.LOGIN_REDIRECT_URL) # Przekieruj na stronę główną
                except User.DoesNotExist:
                     messages.error(request, 'Wystąpił błąd podczas logowania. Użytkownik nie istnieje.')
                     # Usuwamy sesję 2FA, bo jest coś nie tak
                     request.session.pop('2fa_user_pk', None)
                     request.session.pop('2fa_pin_hash', None)
                     request.session.pop('2fa_expiry', None)
                     request.session.pop('2fa_email', None)
                     return redirect('login')
            else:
                # Błędny PIN
                messages.error(request, 'Wprowadzony kod PIN jest nieprawidłowy. Spróbuj ponownie.')
                # Pozostajemy na stronie weryfikacji, formularz będzie pusty
                form = PinVerificationForm() # Resetujemy formularz
        # Jeśli formularz PINu jest niepoprawny (np. nie 4 cyfry), błędy wyświetlą się automatycznie
    else: # Metoda GET
        form = PinVerificationForm() # Pusty formularz dla GET

    # Przekazujemy email do szablonu, aby przypomnieć użytkownikowi, gdzie szukać kodu
    context = {
        'form': form,
        'title': 'Weryfikacja Dwuskładnikowa (2FA)',
        'user_email': user_email
    }
    return render(request, 'users/pin_verification.html', context)

def resend_pin_view(request):
    user_pk = request.session.get('2fa_user_pk')
    user_email = request.session.get('2fa_email')

    if not user_pk or not user_email:
        messages.error(request, 'Nie znaleziono aktywnej sesji weryfikacji do ponownego wysłania kodu.')
        return redirect('login')

    # TODO: Dodać Rate Limiting (np. sprawdzać czas ostatniego wysłania zapisany w sesji)
    # np. last_sent = request.session.get('2fa_last_sent')
    # if last_sent and timezone.now() < timezone.datetime.fromisoformat(last_sent) + timedelta(seconds=60):
    #     messages.warning(request, 'Możesz wysłać kod ponownie za minutę.')
    #     return redirect('pin_verification')

    try:
        user = User.objects.get(pk=user_pk)
        # Wygeneruj nowy PIN, zapisz w sesji, wyślij email
        pin = str(random.randint(1000, 9999)).zfill(4)
        pin_expiry = timezone.now() + timedelta(minutes=10)
        pin_hash = make_password(pin)

        request.session['2fa_pin_hash'] = pin_hash
        request.session['2fa_expiry'] = pin_expiry.isoformat()
        # request.session['2fa_last_sent'] = timezone.now().isoformat() # Zapisz czas wysłania dla rate limiting

        email_context = {'pin': pin, 'user': user}
        subject = 'Twój nowy kod weryfikacyjny UAIS'
        body = render_to_string('users/emails/2fa_pin_email.txt', email_context)
        email_message = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
        email_message.send(fail_silently=False)

        messages.info(request, f'Nowy kod PIN został wysłany na adres {user_email}.')
    except User.DoesNotExist:
         messages.error(request, 'Nie można znaleźć użytkownika do ponownego wysłania kodu.')
         # Czyścimy sesję 2FA? Raczej tak.
         request.session.pop('2fa_user_pk', None)
         request.session.pop('2fa_pin_hash', None)
         request.session.pop('2fa_expiry', None)
         request.session.pop('2fa_email', None)
         return redirect('login')
    except Exception as e:
         messages.error(request, f'Wystąpił błąd podczas wysyłania nowego kodu PIN: {e}')
         # Nie przekierowuj, aby użytkownik widział błąd

    return redirect('pin_verification') # Wróć na stronę weryfikacji PIN

