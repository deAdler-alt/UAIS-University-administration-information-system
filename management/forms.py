# management/forms.py
from django import forms
from users.models import User

# --- Formularz Tworzenia Użytkownika ---
class UserCreateForm(forms.ModelForm):
    # Definicja pól hasła - OK
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Potwierdź hasło', widget=forms.PasswordInput)

    class Meta:
        model = User # Wskazujemy model
        fields = ['email', 'username', 'first_name', 'last_name', 'role', 'rada_wydzialu', 'is_active', 'password', 'password_confirm']
        labels = {
            'is_active': 'Konto aktywne?'
        }
        help_texts = {
            'is_active': 'Odznacz, aby dezaktywować konto bez usuwania go.',
            'username': 'Unikalna nazwa użytkownika (może być wymagana przez system).'
        }

    # Metoda walidacji haseł - umieszczona Wewnątrz UserCreateForm
    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Wprowadzone hasła różnią się.")
        return password_confirm

    # Metoda zapisu z hashowaniem hasła - umieszczona Wewnątrz UserCreateForm
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Hashowanie
        if commit:
            user.save()
        return user

# --- Formularz Edycji Użytkownika ---
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'role', 'rada_wydzialu', 'is_active']
        labels = {
            'is_active': 'Konto aktywne?'
        }
        help_texts = {
            'is_active': 'Odznacz, aby dezaktywować konto bez usuwania go.',
            'username': 'Unikalna nazwa użytkownika.'
        }