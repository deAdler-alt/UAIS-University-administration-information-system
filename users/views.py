from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser

@login_required
def home(request):
    if not request.user.role:
        return redirect('no_role')

    # Definicja menu dla każdej roli
    menu_items = {
        'ADMIN': [
            {'name': 'Pulpit', 'url': '/dashboard/', 'submenu': [
                {'name': 'Zarządzanie użytkownikami', 'url': '/manage_users/', 'allowed_roles': ['ADMIN']},
                {'name': 'Ustawienia systemu', 'url': '/system_settings/', 'allowed_roles': ['ADMIN']},
                {'name': 'Raporty', 'url': '/reports/', 'allowed_roles': ['ADMIN']},
            ]},
            {'name': 'Aktualności', 'url': '/news/', 'submenu': [
                {'name': 'Najnowsze aktualizacje', 'url': '/news/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Katalog', 'url': '/catalog/', 'submenu': [
                {'name': 'Wyszukiwanie', 'url': '/catalog/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Administracja', 'url': '#', 'submenu': [
                {'name': 'Zarządzanie użytkownikami', 'url': '/manage_users/', 'allowed_roles': ['ADMIN']},
                {'name': 'Ustawienia systemu', 'url': '/system_settings/', 'allowed_roles': ['ADMIN']},
                {'name': 'Raporty', 'url': '/reports/', 'allowed_roles': ['ADMIN']},
            ]},
            {'name': 'Narzędzia', 'url': '#', 'submenu': [
                {'name': 'Eksport danych', 'url': '/export_data/', 'allowed_roles': ['ADMIN']},
                {'name': 'Import danych', 'url': '/import_data/', 'allowed_roles': ['ADMIN']},
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
            {'name': 'Pulpit', 'url': '/dashboard/', 'submenu': [
                {'name': 'Przeglądaj dokumenty', 'url': '/legal_docs/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Dodaj dokument', 'url': '/add_doc/', 'allowed_roles': ['PRAWNIK']},
            ]},
            {'name': 'Aktualności', 'url': '/news/', 'submenu': [
                {'name': 'Najnowsze aktualizacje', 'url': '/news/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Katalog', 'url': '/catalog/', 'submenu': [
                {'name': 'Wyszukiwanie', 'url': '/catalog/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Dokumenty prawne', 'url': '#', 'submenu': [
                {'name': 'Przeglądaj dokumenty', 'url': '/legal_docs/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Dodaj dokument', 'url': '/add_doc/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Archiwum dokumentów', 'url': '/archive_docs/', 'allowed_roles': ['PRAWNIK']},
            ]},
            {'name': 'Współpraca', 'url': '#', 'submenu': [
                {'name': 'Wnioski o opinię prawną', 'url': '/legal_requests/', 'allowed_roles': ['PRAWNIK']},
                {'name': 'Historia opinii', 'url': '/legal_history/', 'allowed_roles': ['PRAWNIK']},
            ]},
            {'name': 'Dla wszystkich', 'url': '/for_everyone/', 'submenu': [
                {'name': 'Informacje o radzie wydziału', 'url': '/for_everyone/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
        ],
        'OBSLUGA': [
            {'name': 'Pulpit', 'url': '/dashboard/', 'submenu': [
                {'name': 'Przeglądaj wnioski', 'url': '/view_requests/', 'allowed_roles': ['OBSLUGA']},
                {'name': 'Harmonogram wydarzeń', 'url': '/schedule/', 'allowed_roles': ['OBSLUGA']},
            ]},
            {'name': 'Aktualności', 'url': '/news/', 'submenu': [
                {'name': 'Najnowsze aktualizacje', 'url': '/news/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Katalog', 'url': '/catalog/', 'submenu': [
                {'name': 'Wyszukiwanie', 'url': '/catalog/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Obsługa wniosków', 'url': '#', 'submenu': [
                {'name': 'Przeglądaj wnioski', 'url': '/view_requests/', 'allowed_roles': ['OBSLUGA']},
                {'name': 'Obsłuż wniosek', 'url': '/handle_request/', 'allowed_roles': ['OBSLUGA']},
                {'name': 'Archiwum wniosków', 'url': '/archive_requests/', 'allowed_roles': ['OBSLUGA']},
            ]},
            {'name': 'Organizacja', 'url': '#', 'submenu': [
                {'name': 'Harmonogram wydarzeń', 'url': '/schedule/', 'allowed_roles': ['OBSLUGA']},
                {'name': 'Komunikaty', 'url': '/announcements/', 'allowed_roles': ['OBSLUGA']},
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
            {'name': 'Pulpit', 'url': '/dashboard/', 'submenu': [
                {'name': 'Plan posiedzeń', 'url': '/meeting_plan/', 'allowed_roles': ['RADA']},
                {'name': 'Dodaj uchwałę', 'url': '/add_resolution/', 'allowed_roles': ['RADA']},
            ]},
            {'name': 'Aktualności', 'url': '/news/', 'submenu': [
                {'name': 'Najnowsze aktualizacje', 'url': '/news/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Katalog', 'url': '/catalog/', 'submenu': [
                {'name': 'Wyszukiwanie', 'url': '/catalog/', 'allowed_roles': ['ADMIN', 'PRAWNIK', 'OBSLUGA', 'RADA']},
            ]},
            {'name': 'Posiedzenia rady', 'url': '#', 'submenu': [
                {'name': 'Plan posiedzeń', 'url': '/meeting_plan/', 'allowed_roles': ['RADA']},
                {'name': 'Protokoły', 'url': '/protocols/', 'allowed_roles': ['RADA']},
                {'name': 'Dodaj uchwałę', 'url': '/add_resolution/', 'allowed_roles': ['RADA']},
            ]},
            {'name': 'Dokumenty', 'url': '#', 'submenu': [
                {'name': 'Przeglądaj uchwały', 'url': '/view_resolutions/', 'allowed_roles': ['RADA']},
                {'name': 'Archiwum uchwał', 'url': '/archive_resolutions/', 'allowed_roles': ['RADA']},
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
    context = {
        'message': 'Witaj w SIAU!',
        'menu': menu_items.get(user_role, []),
    }
    return render(request, 'home.html', context)

def no_role(request):
    return render(request, 'no_role.html', {'message': 'Brak przypisanej roli. Skontaktuj się z administratorem.'})

@login_required
def access_denied(request):
    return render(request, 'access_denied.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'message': 'Pulpit - szybki dostęp do funkcji'})

@login_required
def news(request):
    return render(request, 'news.html', {'message': 'Najnowsze aktualizacje na serwisie'})

@login_required
def catalog(request):
    return render(request, 'catalog.html', {'message': 'Katalog wydziału - wyszukiwanie jednostek i osób'})

@login_required
def for_everyone(request):
    return render(request, 'for_everyone.html', {'message': 'Informacje o radzie wydziału'})

@login_required
def manage_users(request):
    if request.user.role != 'ADMIN':
        return redirect('access_denied')
    users = CustomUser.objects.all()
    return render(request, 'manage_users.html', {'users': users})

@login_required
def edit_user(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('access_denied')
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
        return redirect('access_denied')
    user = get_object_or_404(CustomUser, id=user_id)
    if request.user.id != user.id:  # Nie można usunąć samego siebie
        user.delete()
    return redirect('manage_users')

@login_required
def system_settings(request):
    if request.user.role != 'ADMIN':
        return redirect('access_denied')
    return render(request, 'system_settings.html', {'message': 'Ustawienia systemu - tylko dla ADMIN'})

@login_required
def reports(request):
    if request.user.role != 'ADMIN':
        return redirect('access_denied')
    return render(request, 'reports.html', {'message': 'Raporty - tylko dla ADMIN'})

@login_required
def export_data(request):
    if request.user.role != 'ADMIN':
        return redirect('access_denied')
    return render(request, 'export_data.html', {'message': 'Eksport danych - tylko dla ADMIN'})

@login_required
def import_data(request):
    if request.user.role != 'ADMIN':
        return redirect('access_denied')
    return render(request, 'import_data.html', {'message': 'Import danych - tylko dla ADMIN'})

@login_required
def legal_docs(request):
    if request.user.role != 'PRAWNIK':
        return redirect('access_denied')
    return render(request, 'legal_docs.html', {'message': 'Przeglądaj dokumenty prawne - tylko dla PRAWNIK'})

@login_required
def add_doc(request):
    if request.user.role != 'PRAWNIK':
        return redirect('access_denied')
    return render(request, 'add_doc.html', {'message': 'Dodaj nowy dokument - tylko dla PRAWNIK'})

@login_required
def archive_docs(request):
    if request.user.role != 'PRAWNIK':
        return redirect('access_denied')
    return render(request, 'archive_docs.html', {'message': 'Archiwum dokumentów - tylko dla PRAWNIK'})

@login_required
def legal_requests(request):
    if request.user.role != 'PRAWNIK':
        return redirect('access_denied')
    return render(request, 'legal_requests.html', {'message': 'Wnioski o opinię prawną - tylko dla PRAWNIK'})

@login_required
def legal_history(request):
    if request.user.role != 'PRAWNIK':
        return redirect('access_denied')
    return render(request, 'legal_history.html', {'message': 'Historia opinii - tylko dla PRAWNIK'})

@login_required
def view_requests(request):
    if request.user.role != 'OBSLUGA':
        return redirect('access_denied')
    return render(request, 'view_requests.html', {'message': 'Przeglądaj wnioski - tylko dla OBSLUGA'})

@login_required
def handle_request(request):
    if request.user.role != 'OBSLUGA':
        return redirect('access_denied')
    return render(request, 'handle_request.html', {'message': 'Obsłuż wniosek - tylko dla OBSLUGA'})

@login_required
def archive_requests(request):
    if request.user.role != 'OBSLUGA':
        return redirect('access_denied')
    return render(request, 'archive_requests.html', {'message': 'Archiwum wniosków - tylko dla OBSLUGA'})

@login_required
def schedule(request):
    if request.user.role != 'OBSLUGA':
        return redirect('access_denied')
    return render(request, 'schedule.html', {'message': 'Harmonogram wydarzeń - tylko dla OBSLUGA'})

@login_required
def announcements(request):
    if request.user.role != 'OBSLUGA':
        return redirect('access_denied')
    return render(request, 'announcements.html', {'message': 'Komunikaty - tylko dla OBSLUGA'})

@login_required
def meeting_plan(request):
    if request.user.role != 'RADA':
        return redirect('access_denied')
    return render(request, 'meeting_plan.html', {'message': 'Plan posiedzeń - tylko dla RADA'})

@login_required
def protocols(request):
    if request.user.role != 'RADA':
        return redirect('access_denied')
    return render(request, 'protocols.html', {'message': 'Protokoły posiedzeń - tylko dla RADA'})

@login_required
def add_resolution(request):
    if request.user.role != 'RADA':
        return redirect('access_denied')
    return render(request, 'add_resolution.html', {'message': 'Dodaj uchwałę - tylko dla RADA'})

@login_required
def view_resolutions(request):
    if request.user.role != 'RADA':
        return redirect('access_denied')
    return render(request, 'view_resolutions.html', {'message': 'Przeglądaj uchwały - tylko dla RADA'})

@login_required
def archive_resolutions(request):
    if request.user.role != 'RADA':
        return redirect('access_denied')
    return render(request, 'archive_resolutions.html', {'message': 'Archiwum uchwał - tylko dla RADA'})