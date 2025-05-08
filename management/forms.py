# management/forms.py
from django import forms
# Importujemy wszystkie potrzebne modele z users
from users.models import (
    User, Wydzial, RadaDyscypliny,
    Osoba, Funkcja_czlonka, SkladRD, Adres # Dodano Adres
)
from django.forms.widgets import DateInput, Select # Dodano Select

# --- Formularz Tworzenia Użytkownika ---
class UserCreateForm(forms.ModelForm):
    # ... (kod bez zmian) ...
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
    # ... (kod bez zmian) ...
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


# --- Formularz dla Składu Rady Dyscypliny ---
class SkladRDForm(forms.ModelForm):
    # ... (kod bez zmian) ...
    rd = forms.ModelChoiceField(
        queryset=RadaDyscypliny.objects.all().select_related('wydzial').order_by('wydzial__nazwa', 'nazwa'),
        label="Rada Dyscypliny",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    osoba = forms.ModelChoiceField(
        queryset=Osoba.objects.all().order_by('nazwisko', 'imie'),
        label="Osoba (Członek Rady)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    funkcja_czlonka = forms.ModelChoiceField(
        queryset=Funkcja_czlonka.objects.all().order_by('nazwa'),
        label="Funkcja w Radzie",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data_powolania = forms.DateField(
        label="Data powołania", required=False,
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    aktywny = forms.BooleanField(
        label="Członkostwo aktywne", required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = SkladRD
        fields = ['rd', 'osoba', 'funkcja_czlonka', 'data_powolania', 'aktywny']

    def clean(self):
        cleaned_data = super().clean()
        rd = cleaned_data.get("rd")
        osoba = cleaned_data.get("osoba")
        if rd and osoba and not self.instance.pk:
            if SkladRD.objects.filter(rd=rd, osoba=osoba).exists():
                raise forms.ValidationError(
                    f"Osoba {osoba} jest już przypisana do składu Rady Dyscypliny {rd}."
                )
        return cleaned_data


# --- NOWY Formularz dla Osoby ---
class OsobaForm(forms.ModelForm):
    # Jawna definicja pól dla lepszej kontroli i dodania widgetów
    imie = forms.CharField(label="Imię", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nazwisko = forms.CharField(label="Nazwisko", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tytul_stopien = forms.CharField(label="Tytuł/Stopień naukowy (przed nazwiskiem)", max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Adres email", max_length=255, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    stanowisko = forms.CharField(label="Stanowisko", max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefon = forms.CharField(label="Telefon", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    link_do_profilu_nauka_polska = forms.URLField(label="Link do profilu Nauka Polska/ORCID itp.", max_length=255, required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    specjalnosci = forms.CharField(label="Specjalności naukowe", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    plec = forms.ChoiceField(label="Płeć", choices=Osoba.PLEC_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    tytul_po = forms.CharField(label="Tytuł/Stopień (po nazwisku)", max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    # Pola odmian - można użyć TextInput lub Textarea
    imie_nazwisko_dopelniacz = forms.CharField(label="Dopełniacz (kogo, czego?)", max_length=510, widget=forms.TextInput(attrs={'class': 'form-control'}))
    imie_nazwisko_celownik = forms.CharField(label="Celownik (komu, czemu?)", max_length=510, widget=forms.TextInput(attrs={'class': 'form-control'}))
    imie_nazwisko_biernik = forms.CharField(label="Biernik (kogo, co?)", max_length=510, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Osoba
        # Lista pól do uwzględnienia w formularzu (bez 'adresy', bo to ManyToMany)
        fields = [
            'imie', 'nazwisko', 'tytul_stopien', 'email', 'stanowisko', 'telefon',
            'link_do_profilu_nauka_polska', 'specjalnosci', 'plec', 'tytul_po',
            'imie_nazwisko_dopelniacz', 'imie_nazwisko_celownik', 'imie_nazwisko_biernik'
        ]
        # Etykiety i teksty pomocnicze można dostosować, jeśli domyślne z modelu nie wystarczą
        # labels = { ... }
        # help_texts = { ... }

    def clean_email(self):
        # Dodatkowa walidacja unikalności emaila (oprócz tej w modelu)
        email = self.cleaned_data.get('email')
        # Sprawdzamy, czy email już istnieje dla INNEJ osoby niż edytowana
        if Osoba.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Osoba z tym adresem email już istnieje.")
        return email