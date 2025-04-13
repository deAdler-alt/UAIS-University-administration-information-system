# users/urls.py (POPRAWIONA WERSJA)

from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
# Upewnij się, że importujesz wszystkie potrzebne widoki ze swojego pliku views.py
from . import views

urlpatterns = [
    # Logowanie i 2FA
    path('login/', views.login_choice_view, name='login'), # Strona wyboru metody logowania
    path('login/process/', views.process_local_login_view, name='login_process'), # Przetwarzanie loginu lokalnego -> wysyłka PIN
    path('verify-pin/', views.pin_verification_view, name='pin_verification'), # Strona weryfikacji PIN
    path('resend-pin/', views.resend_pin_view, name='resend_pin'), # Ścieżka do ponownego wysłania PIN

    # Wylogowanie
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # Używa LOGOUT_REDIRECT_URL z settings

    # Resetowanie Hasła (gdy użytkownik nie jest zalogowany)
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_done')
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Zmiana Hasła (gdy użytkownik jest zalogowany)
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html',
             success_url=reverse_lazy('password_change_done') # Używamy tego URL
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html' # Nasz szablon z linkiem/formularzem wylogowania
         ),
         name='password_change_done'),

    #  placeholder dla CAS
path('login/cas/', lambda request: redirect('home'), name='cas_login_placeholder'),
]