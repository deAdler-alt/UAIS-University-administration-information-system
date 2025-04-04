from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def home(request):
    if not request.user.role:  # Sprawdzamy, czy rola jest ustawiona
        return HttpResponseForbidden("Brak przypisanej roli. Skontaktuj się z administratorem.")

    menu_items = {
        'ADMIN': [
            {'name': 'Administracja', 'url': '#', 'submenu': [
                {'name': 'Zarządzanie użytkownikami', 'url': '/admin/', 'allowed_roles': ['ADMIN']},
                {'name': 'Sekcja administracyjna', 'url': '/admin_section/', 'allowed_roles': ['ADMIN']},
            ]},
        ],
        'PRAWNIK': [
            {'name': 'Dokumenty prawne', 'url': '#', 'submenu': [
                {'name': 'Przeglądaj dokumenty', 'url': '/legal_docs/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Dodaj dokument', 'url': '/add_doc/', 'allowed_roles': ['PRAWNIK']},
            ]},
        ],
        'OBSLUGA': [
            {'name': 'Obsługa wniosków', 'url': '#', 'submenu': [
                {'name': 'Przeglądaj wnioski', 'url': '/view_requests/', 'allowed_roles': ['OBSLUGA']},
                {'name': 'Obsłuż wniosek', 'url': '/handle_request/', 'allowed_roles': ['OBSLUGA']},
            ]},
        ],
        'RADA': [
            {'name': 'Posiedzenia rady', 'url': '#', 'submenu': [
                {'name': 'Plan posiedzeń', 'url': '/meeting_plan/', 'allowed_roles': ['RADA']},
                {'name': 'Protokoły', 'url': '/protocols/', 'allowed_roles': ['RADA']},
            ]},
        ],
    }
    user_role = request.user.role
    context = {
        'message': 'Witaj w SIAU!',
        'menu': [{'name': item['name'], 'url': item['url'], 'submenu': item.get('submenu', []), 'disabled': False} for item in menu_items.get(user_role, [])],
    }
    return render(request, 'home.html', context)