from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    menu_items = {
        'ADMIN': [
            {'name': 'Zarządzanie użytkownikami', 'url': '/admin/'},
            {'name': 'Sekcja administracyjna', 'url': '#'},
        ],
        'PRAWNIK': [
            {'name': 'Dokumenty prawne', 'url': '#'},
        ],
        'OBSLUGA': [
            {'name': 'Obsługa wniosków', 'url': '#'},
        ],
        'RADA': [
            {'name': 'Posiedzenia rady', 'url': '#'},
        ],
    }
    user_role = request.user.role
    context = {
        'message': 'Witaj w SIAU!',
        'menu': menu_items.get(user_role, []),
    }
    return render(request, 'home.html', context)