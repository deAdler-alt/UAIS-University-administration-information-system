# users/views.py
from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required # Odkomentuj, jeśli potrzebne
from django.contrib.auth.forms import AuthenticationForm # Ten import jest dla login_choice_view

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
def login_choice_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm()
    context = {
        'form': form,
        'title': 'Wybierz Metodę Logowania'
    }
    return render(request, 'users/login_choice.html', context)