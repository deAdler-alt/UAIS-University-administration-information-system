from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('username')  # Pole zawiera e-mail
        password = request.POST.get('password')

        # Znajdź użytkownika po e-mailu
        try:
            user = CustomUser.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                if user.role:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Użytkownik nie posiada przypisanej roli. Skontaktuj się z administratorem serwisu: admin@edu.pl')
            else:
                messages.error(request, 'Błąd logowania: Nieprawidłowe hasło. Sprawdź hasło i spróbuj ponownie.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Błąd logowania: Użytkownik o podanym e-mailu nie istnieje. Sprawdź e-mail i spróbuj ponownie.')
    return render(request, 'registration/login.html')

@login_required
def dashboard(request):
    if not request.user.role:
        messages.error(request, 'Użytkownik nie posiada przypisanej roli. Skontaktuj się z administratorem serwisu: admin@edu.pl')
        return redirect('login')

    # Definicja menu dla każdej roli
    menu_items = {
        'ADMIN': [
            {'name': 'Aktualności', 'url': '/dashboard/', 'submenu': [
                {'name': 'Zarządzanie użytkownikami', 'url': '/manage_users/', 'allowed_roles': ['ADMIN']},
            ]},
            {'name': 'Katalog', 'url': '/catalog/', 'submenu': [
                {'name': 'Wyszukiwanie', 'url': '/catalog/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Administracja', 'url': '#', 'submenu': [
                {'name': 'Zarządzanie użytkownikami', 'url': '/manage_users/', 'allowed_roles': ['ADMIN']},
            ]},
            {'name': 'Dokumenty prawne', 'url': '#', 'submenu': [
                {'name': 'Przeglądaj dokumenty', 'url': '/legal_docs/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Dodaj dokument', 'url': '/add_doc/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Archiwum dokumentów', 'url': '/archive_docs/', 'allowed_roles': ['PRAWNIK']},
            ]},
            {'name': 'Dla wszystkich', 'url': '/for_everyone/', 'submenu': [
                {'name': 'Informacje o radzie wydziału', 'url': '/for_everyone/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
        ],
        'PRAWNIK': [
            {'name': 'Aktualności', 'url': '/dashboard/', 'submenu': [
                {'name': 'Przeglądaj dokumenty', 'url': '/legal_docs/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Dodaj dokument', 'url': '/add_doc/', 'allowed_roles': ['PRAWNIK']},
            ]},
            {'name': 'Katalog', 'url': '/catalog/', 'submenu': [
                {'name': 'Wyszukiwanie', 'url': '/catalog/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Dokumenty prawne', 'url': '#', 'submenu': [
                {'name': 'Przeglądaj dokumenty', 'url': '/legal_docs/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Dodaj dokument', 'url': '/add_doc/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Archiwum dokumentów', 'url': '/archive_docs/', 'allowed_roles': ['PRAWNIK']},
            ]},
            {'name': 'Dla wszystkich', 'url': '/for_everyone/', 'submenu': [
                {'name': 'Informacje o radzie wydziału', 'url': '/for_everyone/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
        ],
        'OBSLUGA': [
            {'name': 'Aktualności', 'url': '/dashboard/', 'submenu': []},
            {'name': 'Katalog', 'url': '/catalog/', 'submenu': [
                {'name': 'Wyszukiwanie', 'url': '/catalog/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Dokumenty prawne', 'url': '#', 'submenu': [
                {'name': 'Przeglądaj dokumenty', 'url': '/legal_docs/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Dodaj dokument', 'url': '/add_doc/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Archiwum dokumentów', 'url': '/archive_docs/', 'allowed_roles': ['PRAWNIK']},
            ]},
            {'name': 'Dla wszystkich', 'url': '/for_everyone/', 'submenu': [
                {'name': 'Informacje o radzie wydziału', 'url': '/for_everyone/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
        ],
        'RADA': [
            {'name': 'Aktualności', 'url': '/dashboard/', 'submenu': []},
            {'name': 'Katalog', 'url': '/catalog/', 'submenu': [
                {'name': 'Wyszukiwanie', 'url': '/catalog/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Dokumenty prawne', 'url': '#', 'submenu': [
                {'name': 'Przeglądaj dokumenty', 'url': '/legal_docs/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Dodaj dokument', 'url': '/add_doc/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Archiwum dokumentów', 'url': '/archive_docs/', 'allowed_roles': ['PRAWNIK']},
            ]},
            {'name': 'Dla wszystkich', 'url': '/for_everyone/', 'submenu': [
                {'name': 'Informacje o radzie wydziału', 'url': '/for_everyone/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
        ],
    }
    user_role = request.user.role
    user_menu = menu_items.get(user_role, [])
    # Przygotuj listę funkcji do wyświetlenia na pulpicie
    dashboard_items = next((item for item in user_menu if item['name'] == 'Aktualności'), {}).get('submenu', [])
    # Przykładowe aktualności
    updates = [
        {'date': '2025-04-05', 'title': 'Nowa wersja systemu SIAU', 'content': 'Wprowadziliśmy nową wersję systemu z poprawionym interfejsem logowania.'},
        {'date': '2025-04-01', 'title': 'Aktualizacja zasad bezpieczeństwa', 'content': 'Zaktualizowaliśmy zasady bezpieczeństwa. Prosimy o zapoznanie się z nowymi wytycznymi.'},
    ]
    context = {
        'message': 'Aktualności - Najnowsze aktualizacje na serwisie',
        'menu': user_menu,
        'dashboard_items': dashboard_items,
        'updates': updates,
    }
    return render(request, 'dashboard.html', context)

@login_required
def catalog(request):
    return render(request, 'catalog.html', {'message': 'Katalog wydziału - wyszukiwanie jednostek i osób'})

@login_required
def for_everyone(request):
    return render(request, 'for_everyone.html', {'message': 'Informacje o radzie wydziału'})

@login_required
def manage_users(request):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')
    users = CustomUser.objects.all()
    return render(request, 'manage_users.html', {'users': users})

@login_required
def edit_user(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.save()
        return redirect('manage_users')
    return render(request, 'edit_user.html', {'user': user})

@login_required
def delete_user(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, id=user_id)
    if request.user.id != user.id:  # Nie można usunąć samego siebie
        user.delete()
    return redirect('manage_users')

@login_required
def legal_docs(request):
    if request.user.role != 'PRAWNIK':
        return redirect('dashboard')
    return render(request, 'legal_docs.html', {'message': 'Przeglądaj dokumenty prawne - tylko dla PRAWNIK'})

@login_required
def add_doc(request):
    if request.user.role != 'PRAWNIK':
        return redirect('dashboard')
    return render(request, 'add_doc.html', {'message': 'Dodaj nowy dokument - tylko dla PRAWNIK'})

@login_required
def archive_docs(request):
    if request.user.role != 'PRAWNIK':
        return redirect('dashboard')
    return render(request, 'archive_docs.html', {'message': 'Archiwum dokumentów - tylko dla PRAWNIK'})