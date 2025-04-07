# users/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Opcjonalnie, jeśli strona główna wymaga zalogowania

# Widok strony logowania (już go nie potrzebujemy definiować, bo używamy auth_views.LoginView)
# def login_view(request):
#    pass

# Widok strony głównej
# @login_required # Odkomentuj, jeśli chcesz, aby dostęp był tylko dla zalogowanych
def home_view(request):
    context = {
        'welcome_message': 'Witaj w systemie UAIS!',
    }
    # Użyjemy szablonu 'home.html', który będzie w głównym folderze templates
    return render(request, 'home.html', context)