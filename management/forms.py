# management/forms.py
from django import forms
from users.models import User, Wydzial, RadaDyscypliny # Dodano import Wydzial i RadaDyscypliny

# --- Formularz Tworzenia Użytkownika ---
class UserCreateForm(forms.ModelForm):
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Potwierdź hasło', widget=forms.PasswordInput)

    # Definicja nowych pól wyboru
    wydzial = forms.ModelChoiceField(
        queryset=Wydzial.objects.all(),
        required=False, # Ustaw na True, jeśli Wydział jest zawsze wymagany
        label="Wydział",
        help_text="Wybierz wydział użytkownika."
    )
    rada_dyscypliny_fk = forms.ModelChoiceField(
        queryset=RadaDyscypliny.objects.none(), # Początkowo puste, ładowane przez JS
        required=False, # Ustaw na True, jeśli Rada Dyscypliny jest zawsze wymagana
        label="Rada Dyscypliny",
        help_text="Wybierz radę dyscypliny (dostępne po wybraniu wydziału)."
    )

    class Meta:
        model = User
        # Zaktualizowana lista pól: usunięto 'username' i stare 'rada_wydzialu',
        # dodano nowe 'wydzial' i 'rada_dyscypliny_fk'
        fields = ['email', 'first_name', 'last_name', 'role', 'wydzial', 'rada_dyscypliny_fk', 'is_active', 'password', 'password_confirm']
        labels = {
            'is_active': 'Konto aktywne?',
            'email': 'Adres email (login)',
        }
        help_texts = {
            'is_active': 'Odznacz, aby dezaktywować konto bez usuwania go.',
            'email': 'Adres email będzie używany jako login użytkownika.'
            # Usunięto help_text dla 'username'
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Wprowadzone hasła różnią się.")
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    # Dodajemy __init__ do UserCreateForm, aby obsłużyć queryset dla rada_dyscypliny_fk
    # w przypadku, gdy formularz jest renderowany z błędami i wartościami POST
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'wydzial' in self.data: # Jeśli formularz jest przesyłany z danymi
            try:
                wydzial_id = int(self.data.get('wydzial'))
                self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial_id=wydzial_id).order_by('nazwa')
            except (ValueError, TypeError):
                pass # wydzial_id jest niepoprawny, queryset pozostaje .none()
        elif self.instance and self.instance.pk and self.instance.wydzial: # Jeśli edytujemy instancję, która ma już wydział
            self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial=self.instance.wydzial).order_by('nazwa')


# --- Formularz Edycji Użytkownika ---
class UserUpdateForm(forms.ModelForm):
    # Definicja nowych pól wyboru
    wydzial = forms.ModelChoiceField(
        queryset=Wydzial.objects.all(),
        required=False,
        label="Wydział",
        help_text="Wybierz wydział użytkownika."
    )
    rada_dyscypliny_fk = forms.ModelChoiceField(
        queryset=RadaDyscypliny.objects.none(), # Początkowo puste, ładowane przez JS
        required=False,
        label="Rada Dyscypliny",
        help_text="Wybierz radę dyscypliny (dostępne po wybraniu wydziału)."
    )

    class Meta:
        model = User
        # Zaktualizowana lista pól
        fields = ['email', 'first_name', 'last_name', 'role', 'wydzial', 'rada_dyscypliny_fk', 'is_active']
        labels = {
            'is_active': 'Konto aktywne?',
            'email': 'Adres email (login)',
        }
        help_texts = {
            'is_active': 'Odznacz, aby dezaktywować konto bez usuwania go.',
            'email': 'Adres email będzie używany jako login użytkownika.'
            # Usunięto help_text dla 'username'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Jeśli edytujemy istniejącego użytkownika i ma on już przypisany wydział,
        # wypełniamy queryset dla rad dyscypliny tego wydziału
        if self.instance and self.instance.pk and self.instance.wydzial:
            self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial=self.instance.wydzial).order_by('nazwa')
        # W przeciwnym razie queryset pozostaje .none() (JavaScript zajmie się resztą przy wyborze)