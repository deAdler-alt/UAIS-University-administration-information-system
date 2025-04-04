from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import CustomUser

@login_required
def home(request):
    if not request.user.role:
        return redirect('no_role')

    menu_items = {
        'ADMIN': [
            {'name': 'Administracja', 'url': '#', 'submenu': [
                {'name': 'Zarządzanie użytkownikami', 'url': '/manage_users/', 'allowed_roles': ['ADMIN']},
                {'name': 'Sekcja administracyjna', 'url': '/admin_section/', 'allowed_roles': ['ADMIN']},
            ]},
        ],
    }
    user_role = request.user.role
    context = {
        'message': 'Witaj w SIAU!',
        'menu': [{'name': item['name'], 'url': item['url'], 'submenu': item.get('submenu', []), 'disabled': False} for item in menu_items.get(user_role, [])],
    }
    return render(request, 'home.html', context)

def no_role(request):
    return render(request, 'no_role.html', {'message': 'Brak przypisanej roli. Skontaktuj się z administratorem.'})

@login_required
def admin_section(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Brak dostępu.")
    return render(request, 'admin_section.html', {'message': 'Sekcja administracyjna - tylko dla ADMIN'})

@login_required
def manage_users(request):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("Brak dostępu.")
    users = CustomUser.objects.all()
    return render(request, 'manage_users.html', {'users': users})