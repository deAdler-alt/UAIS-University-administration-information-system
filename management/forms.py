# management/forms.py
from django import forms
# Importujemy wszystkie potrzebne modele z users
from users.models import (
    User, Wydzial, RadaDyscypliny,
    Osoba, Funkcja_czlonka, SkladRD # Dodano Osoba, Funkcja_czlonka, SkladRD
)
from django.forms.widgets import DateInput # Dla ładniejszego pola daty

# --- Formularz Tworzenia Użytkownika ---
class UserCreateForm(forms.ModelForm):
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Potwierdź hasło', widget=forms.PasswordInput)
    wydzial = forms.ModelChoiceField(
        queryset=Wydzial.objects.all(), required=False, label="Wydział",
        help_text="Wybierz wydział użytkownika."
    )
    rada_dyscypliny_fk = forms.ModelChoiceField(
        queryset=RadaDyscypliny.objects.none(), required=False, label="Rada Dyscypliny",
        help_text="Wybierz radę dyscypliny (dostępne po wybraniu wydziału)."
    )
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'wydzial', 'rada_dyscypliny_fk', 'is_active', 'password', 'password_confirm']
        labels = {'is_active': 'Konto aktywne?', 'email': 'Adres email (login)'}
        help_texts = {'is_active': 'Odznacz, aby dezaktywować konto bez usuwania go.', 'email': 'Adres email będzie używany jako login użytkownika.'}

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Wprowadzone hasła różnią się.")
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit: user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'wydzial' in self.data:
            try:
                wydzial_id = int(self.data.get('wydzial'))
                self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial_id=wydzial_id).order_by('nazwa')
            except (ValueError, TypeError): pass
        elif self.instance and self.instance.pk and self.instance.wydzial:
            self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial=self.instance.wydzial).order_by('nazwa')

# --- Formularz Edycji Użytkownika ---
class UserUpdateForm(forms.ModelForm):
    wydzial = forms.ModelChoiceField(
        queryset=Wydzial.objects.all(), required=False, label="Wydział",
        help_text="Wybierz wydział użytkownika."
    )
    rada_dyscypliny_fk = forms.ModelChoiceField(
        queryset=RadaDyscypliny.objects.none(), required=False, label="Rada Dyscypliny",
        help_text="Wybierz radę dyscypliny (dostępne po wybraniu wydziału)."
    )
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'wydzial', 'rada_dyscypliny_fk', 'is_active']
        labels = {'is_active': 'Konto aktywne?', 'email': 'Adres email (login)'}
        help_texts = {'is_active': 'Odznacz, aby dezaktywować konto bez usuwania go.', 'email': 'Adres email będzie używany jako login użytkownika.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.wydzial:
            self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial=self.instance.wydzial).order_by('nazwa')


# --- NOWY Formularz dla Składu Rady Dyscypliny ---
class SkladRDForm(forms.ModelForm):
    # Definiujemy pola jawnie dla lepszej kontroli (np. widgety, querysety)
    rd = forms.ModelChoiceField(
        queryset=RadaDyscypliny.objects.all().select_related('wydzial').order_by('wydzial__nazwa', 'nazwa'),
        label="Rada Dyscypliny",
        widget=forms.Select(attrs={'class': 'form-select'}) # Dodajemy klasę Bootstrap
    )
    osoba = forms.ModelChoiceField(
        queryset=Osoba.objects.all().order_by('nazwisko', 'imie'),
        label="Osoba (Członek Rady)",
        widget=forms.Select(attrs={'class': 'form-select'}) # Dodajemy klasę Bootstrap
        # Można rozważyć widget autocomplete, jeśli lista osób będzie długa
        # np. z django-autocomplete-light lub innym pakietem
    )
    funkcja_czlonka = forms.ModelChoiceField(
        queryset=Funkcja_czlonka.objects.all().order_by('nazwa'),
        label="Funkcja w Radzie",
        widget=forms.Select(attrs={'class': 'form-select'}) # Dodajemy klasę Bootstrap
    )
    data_powolania = forms.DateField(
        label="Data powołania",
        required=False, # Zgodnie z modelem (null=True, blank=True)
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}) # Używamy widgetu HTML5 date
    )
    aktywny = forms.BooleanField(
        label="Członkostwo aktywne",
        required=False, # Checkbox nie wymaga required=True
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}) # Klasa Bootstrap
    )

    class Meta:
        model = SkladRD
        fields = ['rd', 'osoba', 'funkcja_czlonka', 'data_powolania', 'aktywny']
        # Można dodać labels i help_texts, jeśli domyślne z modelu nie wystarczą
        # labels = { ... }
        # help_texts = { ... }

    def clean(self):
        # Dodatkowa walidacja, jeśli potrzebna
        # Np. sprawdzić, czy dana osoba nie jest już w składzie tej rady
        cleaned_data = super().clean()
        rd = cleaned_data.get("rd")
        osoba = cleaned_data.get("osoba")

        # Sprawdź unikalność (rd, osoba) - tylko przy tworzeniu nowego wpisu
        if rd and osoba and not self.instance.pk: # self.instance.pk wskazuje, że edytujemy istniejący obiekt
            if SkladRD.objects.filter(rd=rd, osoba=osoba).exists():
                raise forms.ValidationError(
                    f"Osoba {osoba} jest już przypisana do składu Rady Dyscypliny {rd}."
                )
        # Można dodać więcej reguł walidacji

        return cleaned_data