# management/forms.py (POPRAWIONA WERSJA v2)
from django import forms
from users.models import User # Importujemy NOWY model User

class UserCreateForm(forms.ModelForm):
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Potwierdź hasło', widget=forms.PasswordInput)

    class Meta:
        model = User
        # Pola z NOWEGO modelu User potrzebne przy tworzeniu (bez imie/nazwisko)
        # Dodajemy też pole 'osoba' (OneToOne) - na razie jako wybór, potem to ulepszymy
        fields = ['email', 'aktywny', 'is_staff', 'uprawnienia', 'rd', 'osoba']
        labels = {
            'aktywny': 'Konto aktywne?',
            'is_staff': 'Dostęp do admina Django?'
        }
        help_texts = {
            'aktywny': 'Odznacz, aby dezaktywować konto bez usuwania go.',
            'is_staff': 'Zaznacz, aby dać dostęp do standardowego panelu /admin/ Django.'
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Wprowadzone hasła różnią się.")
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Hashowanie
        # Tutaj brakuje logiki tworzenia/aktualizacji obiektu Osoba
        # Na razie zapisujemy tylko Usera
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # Pola z NOWEGO modelu User do edycji (bez hasła, bez imie/nazwisko)
        fields = ['email', 'aktywny', 'is_staff', 'uprawnienia', 'rd', 'osoba']
        labels = {
            'aktywny': 'Konto aktywne?',
            'is_staff': 'Dostęp do admina Django?'
        }
        help_texts = {
            'aktywny': 'Odznacz, aby dezaktywować konto bez usuwania go.',
            'is_staff': 'Zaznacz, aby dać dostęp do standardowego panelu /admin/ Django.'
        }
        # widgets = { # Można odkomentować, by zablokować edycję emaila
        #     'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        # }