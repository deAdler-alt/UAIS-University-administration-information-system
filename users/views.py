from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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