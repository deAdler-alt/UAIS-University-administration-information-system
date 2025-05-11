# users/views.py

from django.urls import path, reverse_lazy # path nie jest tu potrzebne, ale może być w innych miejscach
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
import random
from datetime import timedelta, datetime # UWAGA: Dodano import datetime
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.conf import settings
from django.contrib import messages
from .forms import PinVerificationForm
# from . import views # Usunięto rekurencyjny import, jeśli 'views' odnosiło się do tego samego pliku

User = get_user_model()


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
    context = {
        'welcome_message': 'Witaj w systemie UAIS!',
        'commits': dummy_commits
    }
    return render(request, 'home.html', context)


def login_choice_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = AuthenticationForm()
    context = {
        'form': form,
        'title': 'Wybierz Metodę Logowania'
    }
    return render(request, 'users/login_choice.html', context)

def process_local_login_view(request):
    if request.user.is_authenticated:
         return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                pin = str(random.randint(1000, 9999)).zfill(4)
                pin_expiry = timezone.now() + timedelta(minutes=10)
                pin_hash = make_password(pin)

                request.session['2fa_user_pk'] = user.pk
                request.session['2fa_pin_hash'] = pin_hash
                request.session['2fa_expiry'] = pin_expiry.isoformat()
                request.session['2fa_email'] = user.email
                # UWAGA: Zapisujemy czas wysłania pierwszego PINu dla rate limiting
                request.session['2fa_last_sent_timestamp'] = timezone.now().isoformat()


                email_context = {'pin': pin, 'user': user}
                subject = 'Twój kod weryfikacyjny UAIS'
                body = render_to_string('users/emails/2fa_pin_email.txt', email_context)
                email_message = EmailMessage(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                email_message.send(fail_silently=False)

                messages.info(request, f'Na adres {user.email} wysłano kod weryfikacyjny PIN.')
                return redirect('pin_verification')

            except Exception as e:
                messages.error(request, f'Wystąpił błąd podczas inicjowania weryfikacji 2FA. Spróbuj ponownie. Błąd: {e}')
                login_form = AuthenticationForm()
                context = {'form': login_form, 'title': 'Wybierz Metodę Logowania'}
                return render(request, 'users/login_choice.html', context)
        else:
            messages.error(request, "Niepoprawny email lub hasło.")
            context = {'form': form, 'title': 'Wybierz Metodę Logowania'}
            return render(request, 'users/login_choice.html', context)
    else:
        return redirect('login')


def pin_verification_view(request):
    user_pk = request.session.get('2fa_user_pk')
    pin_hash = request.session.get('2fa_pin_hash')
    expiry_str = request.session.get('2fa_expiry')
    user_email = request.session.get('2fa_email', 'Twój adres email')

    if not all([user_pk, pin_hash, expiry_str]):
        messages.error(request, 'Sesja weryfikacji wygasła lub jest nieprawidłowa. Zaloguj się ponownie.')
        return redirect('login')

    try:
        # UWAGA: Używamy datetime.fromisoformat() zamiast timezone.datetime.fromisoformat()
        expiry = datetime.fromisoformat(expiry_str)
    except ValueError:
         messages.error(request, 'Błąd formatu czasu sesji weryfikacji. Zaloguj się ponownie.')
         return redirect('login')

    if timezone.now() > expiry:
        request.session.pop('2fa_user_pk', None)
        request.session.pop('2fa_pin_hash', None)
        request.session.pop('2fa_expiry', None)
        request.session.pop('2fa_email', None)
        request.session.pop('2fa_last_sent_timestamp', None) # Czyścimy też czas ostatniego wysłania
        messages.error(request, 'Kod PIN wygasł. Zaloguj się ponownie, aby otrzymać nowy kod.')
        return redirect('login')

    if request.method == 'POST':
        form = PinVerificationForm(request.POST)
        if form.is_valid():
            entered_pin = form.cleaned_data['pin']
            if check_password(entered_pin, pin_hash):
                try:
                    user = User.objects.get(pk=user_pk)
                    auth_login(request, user)
                    request.session.pop('2fa_user_pk', None)
                    request.session.pop('2fa_pin_hash', None)
                    request.session.pop('2fa_expiry', None)
                    request.session.pop('2fa_email', None)
                    request.session.pop('2fa_last_sent_timestamp', None) # Czyścimy też czas ostatniego wysłania
                    messages.success(request, 'Zostałeś pomyślnie zalogowany.')
                    return redirect(settings.LOGIN_REDIRECT_URL)
                except User.DoesNotExist:
                     messages.error(request, 'Wystąpił błąd podczas logowania. Użytkownik nie istnieje.')
                     request.session.pop('2fa_user_pk', None)
                     request.session.pop('2fa_pin_hash', None)
                     request.session.pop('2fa_expiry', None)
                     request.session.pop('2fa_email', None)
                     request.session.pop('2fa_last_sent_timestamp', None)
                     return redirect('login')
            else:
                messages.error(request, 'Wprowadzony kod PIN jest nieprawidłowy. Spróbuj ponownie.')
                form = PinVerificationForm()
        # Błędy formularza PIN (np. nie 4 cyfry) wyświetlą się automatycznie
    else:
        form = PinVerificationForm()

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

    # --- Implementacja Rate Limiting ---
    last_sent_str = request.session.get('2fa_last_sent_timestamp')
    if last_sent_str:
        try:
            # UWAGA: Używamy datetime.fromisoformat()
            last_sent_dt = datetime.fromisoformat(last_sent_str)
            # Upewniamy się, że last_sent_dt jest świadome strefy czasowej, jeśli timezone.now() jest
            if timezone.is_naive(last_sent_dt) and timezone.is_aware(timezone.now()):
                last_sent_dt = timezone.make_aware(last_sent_dt, timezone.get_current_timezone())
            elif timezone.is_aware(last_sent_dt) and timezone.is_naive(timezone.now()):
                 # To nie powinno się zdarzyć, jeśli zawsze używamy timezone.now()
                pass


            if timezone.now() < last_sent_dt + timedelta(seconds=60): # 60 sekund opóźnienia
                time_to_wait = (last_sent_dt + timedelta(seconds=60)) - timezone.now()
                messages.warning(request, f'Możesz wysłać kod ponownie za {time_to_wait.seconds} sekund.')
                return redirect('pin_verification')
        except ValueError:
            # Jeśli data w sesji jest uszkodzona, ignorujemy rate limiting dla tego jednego razu
            pass
    # --- Koniec Rate Limiting ---

    try:
        user = User.objects.get(pk=user_pk)
        pin = str(random.randint(1000, 9999)).zfill(4)
        pin_expiry = timezone.now() + timedelta(minutes=10)
        pin_hash = make_password(pin)

        request.session['2fa_pin_hash'] = pin_hash
        request.session['2fa_expiry'] = pin_expiry.isoformat()
        # UWAGA: Aktualizujemy czas ostatniego wysłania PINu
        request.session['2fa_last_sent_timestamp'] = timezone.now().isoformat()

        email_context = {'pin': pin, 'user': user}
        subject = 'Twój nowy kod weryfikacyjny UAIS'
        body = render_to_string('users/emails/2fa_pin_email.txt', email_context)
        email_message = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
        email_message.send(fail_silently=False)

        messages.info(request, f'Nowy kod PIN został wysłany na adres {user_email}.')
    except User.DoesNotExist:
         messages.error(request, 'Nie można znaleźć użytkownika do ponownego wysłania kodu.')
         request.session.pop('2fa_user_pk', None)
         request.session.pop('2fa_pin_hash', None)
         request.session.pop('2fa_expiry', None)
         request.session.pop('2fa_email', None)
         request.session.pop('2fa_last_sent_timestamp', None) # Czyścimy też czas ostatniego wysłania
         return redirect('login')
    except Exception as e:
         messages.error(request, f'Wystąpił błąd podczas wysyłania nowego kodu PIN: {e}')
         # Nie przekierowujemy, aby użytkownik widział błąd na stronie weryfikacji PIN

    return redirect('pin_verification')
