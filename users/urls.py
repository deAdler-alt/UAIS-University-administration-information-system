# users/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views # Importujemy nasze widoki z users/views.py

# Zmień nazwę głównego URL logowania na 'login_choice', bo LOGIN_URL będzie na to wskazywał?
# Lub pozostaw 'login' dla widoku wyboru. Pozostawmy 'login'.
# app_name = 'users' # Jeśli używasz przestrzeni nazw dla tej aplikacji

urlpatterns = [
    # Główny URL logowania - teraz wyświetla stronę wyboru
    path('login/', views.login_choice_view, name='login'),

    # URL, który faktycznie PRZETWARZA formularz logowania lokalnego
    # Tymczasowo używa LoginView, który przy błędzie ponownie wyświetli stronę wyboru
    # Zmienimy to później przy implementacji 2FA
    path('login/process/',
         auth_views.LoginView.as_view(
             template_name='users/login_choice.html', # Przy błędzie pokaże znów stronę wyboru z błędami formularza
             redirect_authenticated_user=True # Jeśli user jest zalogowany, od razu przekieruj (np. do 'home')
         ),
         name='login_process'),

    # Placeholder dla logowania CAS (na razie nie robi nic lub przekierowuje)
    # path('login/cas/', lambda request: redirect('home'), name='cas_login_placeholder'), # Można dodać później

    # Wylogowanie - bez zmian (używa formularza POST)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Ścieżki Resetowania Hasła - bez zmian
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
]