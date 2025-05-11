# management/forms.py
from django import forms
from users.models import (
    User, Wydzial, RadaDyscypliny,
    Osoba, Funkcja_czlonka, SkladRD, Adres, Doktorant
)
from django.forms.widgets import DateInput # Select jest już importowany przez forms

# --- Formularz Tworzenia Użytkownika ---
class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        label='Hasło', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Hasło musi spełniać odpowiednie kryteria złożoności." # Dodano help_text
    )
    password_confirm = forms.CharField(
        label='Potwierdź hasło', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        label='Adres email (login)', 
        widget=forms.EmailInput(attrs={'class': 'form-control'}), 
        help_text="Adres email będzie używany jako login użytkownika."
    )
    first_name = forms.CharField(
        label='Imię', 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Nazwisko', 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        label='Rola systemowa', 
        choices=User.Role.choices, 
        widget=forms.Select(attrs={'class': 'form-select'}), 
        required=True # Rola jest wymagana przy tworzeniu
    )
    
    wydzial = forms.ModelChoiceField(
        queryset=Wydzial.objects.all().order_by('nazwa'),
        required=False, 
        label="Wydział",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_wydzial_user'})
    )
    rada_dyscypliny_fk = forms.ModelChoiceField(
        queryset=RadaDyscypliny.objects.none(), 
        required=False,
        label="Rada Dyscypliny",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_rada_dyscypliny_fk_user'}),
        help_text="Wybierz radę dyscypliny (dostępne po wybraniu wydziału)."
    )
    is_active = forms.BooleanField(
        label='Konto aktywne?', 
        required=False, 
        initial=True, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        help_text="Odznacz, aby dezaktywować konto bez usuwania go."
    )

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'role', 
            'wydzial', 'rada_dyscypliny_fk', 'is_active', 
            'password', 'password_confirm'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Logika dla dynamicznego ładowania rad dyscypliny
        # Ważne, aby zachować wybrane wartości po stronie serwera w przypadku błędu walidacji
        # lub przy inicjalizacji formularza z danymi (choć to UserCreateForm)
        
        # Jeśli formularz jest wysyłany z danymi i 'wydzial' jest w tych danych
        if 'wydzial' in self.data:
            try:
                wydzial_id = int(self.data.get('wydzial'))
                self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial_id=wydzial_id).order_by('nazwa')
            except (ValueError, TypeError):
                # Jeśli wydzial_id jest niepoprawny, queryset pozostaje pusty
                self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.none()
        # Jeśli formularz jest inicjalizowany z instancją (mniej typowe dla CreateView, ale dla spójności)
        elif self.instance and self.instance.pk and self.instance.wydzial:
            self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial=self.instance.wydzial).order_by('nazwa')
        else:
            # Dla nowego, pustego formularza (nie POST), queryset dla rady pozostaje pusty
            self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.none()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Użytkownik z tym adresem email już istnieje.")
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Wprowadzone hasła różnią się.")
        return password_confirm

    def clean(self):
        cleaned_data = super().clean()
        wydzial = cleaned_data.get('wydzial')
        rada_dyscypliny = cleaned_data.get('rada_dyscypliny_fk')
        role = cleaned_data.get('role')

        if wydzial and rada_dyscypliny:
            if rada_dyscypliny.wydzial != wydzial:
                self.add_error('rada_dyscypliny_fk', "Wybrana Rada Dyscypliny nie należy do wybranego Wydziału.")
        
        if role in [User.Role.RADA, User.Role.OBSLUGA]:
            if not wydzial:
                self.add_error('wydzial', "Dla tej roli Wydział jest wymagany.")
            if not rada_dyscypliny:
                self.add_error('rada_dyscypliny_fk', "Dla tej roli Rada Dyscypliny jest wymagana.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Hasło jest ustawiane tutaj
        if commit:
            user.save()
        return user


# --- Formularz Edycji Użytkownika ---
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label='Adres email (login)', 
        widget=forms.EmailInput(attrs={'class': 'form-control'}), 
        help_text="Adresu email (loginu) nie można zmienić.",
        disabled=True # Ustawiamy pole jako wyłączone w __init__
    )
    first_name = forms.CharField(label='Imię', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Nazwisko', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(label='Rola systemowa', choices=User.Role.choices, widget=forms.Select(attrs={'class': 'form-select'}), required=True)

    wydzial = forms.ModelChoiceField(
        queryset=Wydzial.objects.all().order_by('nazwa'),
        required=False,
        label="Wydział",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_wydzial_user_update'})
    )
    rada_dyscypliny_fk = forms.ModelChoiceField(
        queryset=RadaDyscypliny.objects.none(), 
        required=False,
        label="Rada Dyscypliny",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_rada_dyscypliny_fk_user_update'}),
        help_text="Wybierz radę dyscypliny (dostępne po wybraniu wydziału)."
    )
    is_active = forms.BooleanField(label='Konto aktywne?', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), help_text="Odznacz, aby dezaktywować konto bez usuwania go.")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'wydzial', 'rada_dyscypliny_fk', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True # Wyłączamy pole email

        # Inicjalizacja queryset dla rady dyscypliny na podstawie instancji lub danych POST
        if self.instance and self.instance.pk:
            if self.instance.wydzial:
                self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial=self.instance.wydzial).order_by('nazwa')
                # Nie ustawiamy self.initial['wydzial'] tutaj, bo ModelChoiceField sam to zrobi na podstawie instancji
            else:
                self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.none()
        elif 'wydzial' in self.data: # Dla POST request z wybranym wydziałem
            try:
                wydzial_id = int(self.data.get('wydzial'))
                self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.filter(wydzial_id=wydzial_id).order_by('nazwa')
            except (ValueError, TypeError):
                 self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.none()
        else:
            self.fields['rada_dyscypliny_fk'].queryset = RadaDyscypliny.objects.none()

    def clean_email(self):
        # Email jest disabled, więc jego wartość nie powinna być zmieniana.
        # Zwracamy wartość z instancji, aby uniknąć problemów.
        if self.instance and self.instance.pk:
            return self.instance.email
        return self.cleaned_data.get('email') # Powinno być None lub oryginalna wartość

    def clean(self):
        cleaned_data = super().clean()
        wydzial = cleaned_data.get('wydzial')
        rada_dyscypliny = cleaned_data.get('rada_dyscypliny_fk')
        role = cleaned_data.get('role')

        if wydzial and rada_dyscypliny:
            if rada_dyscypliny.wydzial != wydzial:
                self.add_error('rada_dyscypliny_fk', "Wybrana Rada Dyscypliny nie należy do wybranego Wydziału.")
        
        if role in [User.Role.RADA, User.Role.OBSLUGA]:
            if not wydzial:
                self.add_error('wydzial', "Dla tej roli Wydział jest wymagany.")
            if not rada_dyscypliny:
                self.add_error('rada_dyscypliny_fk', "Dla tej roli Rada Dyscypliny jest wymagana.")
        
        return cleaned_data

# --- Formularz dla Składu Rady Dyscypliny ---
class SkladRDForm(forms.ModelForm):
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
        label="Członkostwo aktywne", required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = SkladRD
        fields = ['rd', 'osoba', 'funkcja_czlonka', 'data_powolania', 'aktywny']

    def clean(self):
        cleaned_data = super().clean()
        rd = cleaned_data.get("rd")
        osoba = cleaned_data.get("osoba")
        
        is_new = self.instance.pk is None
        if rd and osoba: # Sprawdzamy tylko jeśli oba pola są wypełnione
            query = SkladRD.objects.filter(rd=rd, osoba=osoba)
            if is_new:
                if query.exists():
                    raise forms.ValidationError(f"Osoba {osoba} jest już przypisana do składu Rady Dyscypliny {rd}.")
            else: # Edycja
                # Sprawdzamy, czy istnieje inny wpis z tą samą kombinacją osoba-rada
                if query.exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError(f"Kombinacja osoby {osoba} i Rady Dyscypliny {rd} już istnieje dla innego wpisu.")
        return cleaned_data


# --- Formularz dla Osoby ---
class OsobaForm(forms.ModelForm):
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
    imie_nazwisko_dopelniacz = forms.CharField(label="Dopełniacz (kogo, czego?)", max_length=510, widget=forms.TextInput(attrs={'class': 'form-control'}))
    imie_nazwisko_celownik = forms.CharField(label="Celownik (komu, czemu?)", max_length=510, widget=forms.TextInput(attrs={'class': 'form-control'}))
    imie_nazwisko_biernik = forms.CharField(label="Biernik (kogo, co?)", max_length=510, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Osoba
        fields = [
            'imie', 'nazwisko', 'tytul_stopien', 'email', 'stanowisko', 'telefon',
            'link_do_profilu_nauka_polska', 'specjalnosci', 'plec', 'tytul_po',
            'imie_nazwisko_dopelniacz', 'imie_nazwisko_celownik', 'imie_nazwisko_biernik'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Osoba.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Osoba z tym adresem email już istnieje.")
        return email

# --- Formularz dla Doktoranta ---
class DoktorantForm(forms.ModelForm):
    wydzial = forms.ModelChoiceField(
        queryset=Wydzial.objects.all().order_by('nazwa'),
        required=True, 
        label="Wydział",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_wydzial_doktorant'})
    )
    rada_dyscypliny = forms.ModelChoiceField(
        queryset=RadaDyscypliny.objects.none(), 
        required=True, 
        label="Rada Dyscypliny",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_rada_dyscypliny_doktorant'}),
        help_text="Wybierz radę dyscypliny (dostępne po wybraniu wydziału)."
    )
    imie = forms.CharField(label="Imię", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nazwisko = forms.CharField(label="Nazwisko", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Adres email", max_length=255, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    tytul_stopien = forms.CharField(label="Tytuł/Stopień naukowy", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    plec = forms.ChoiceField(label="Płeć", choices=Doktorant.PLEC_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    imie_nazwisko_dopelniacz = forms.CharField(label="Dopełniacz (kogo, czego?)", max_length=510, widget=forms.TextInput(attrs={'class': 'form-control'}))
    imie_nazwisko_celownik = forms.CharField(label="Celownik (komu, czemu?)", max_length=510, widget=forms.TextInput(attrs={'class': 'form-control'}))
    imie_nazwisko_biernik = forms.CharField(label="Biernik (kogo, co?)", max_length=510, widget=forms.TextInput(attrs={'class': 'form-control'}))
    adres_ulica = forms.CharField(label="Ulica", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    adres_kod_pocztowy = forms.CharField(label="Kod pocztowy", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    adres_miasto = forms.CharField(label="Miasto", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefon = forms.CharField(label="Telefon", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Doktorant
        fields = [
            'wydzial', 
            'rada_dyscypliny',
            'imie', 'nazwisko', 'email', 'tytul_stopien', 'plec',
            'imie_nazwisko_dopelniacz', 'imie_nazwisko_celownik', 'imie_nazwisko_biernik',
            'adres_ulica', 'adres_kod_pocztowy', 'adres_miasto', 'telefon',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk: 
            if self.instance.rada_dyscypliny and self.instance.rada_dyscypliny.wydzial:
                self.initial['wydzial'] = self.instance.rada_dyscypliny.wydzial_id
                self.fields['rada_dyscypliny'].queryset = RadaDyscypliny.objects.filter(
                    wydzial_id=self.instance.rada_dyscypliny.wydzial_id
                ).order_by('nazwa')
                self.initial['rada_dyscypliny'] = self.instance.rada_dyscypliny_id
            else:
                self.fields['rada_dyscypliny'].queryset = RadaDyscypliny.objects.none()
        
        elif 'wydzial' in self.data: 
            try:
                wydzial_id = int(self.data.get('wydzial'))
                self.fields['rada_dyscypliny'].queryset = RadaDyscypliny.objects.filter(wydzial_id=wydzial_id).order_by('nazwa')
            except (ValueError, TypeError):
                self.fields['rada_dyscypliny'].queryset = RadaDyscypliny.objects.none()
        else: 
            self.fields['rada_dyscypliny'].queryset = RadaDyscypliny.objects.none()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Doktorant.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Doktorant z tym adresem email już istnieje.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        wydzial = cleaned_data.get('wydzial')
        rada_dyscypliny = cleaned_data.get('rada_dyscypliny')

        if wydzial and rada_dyscypliny:
            if rada_dyscypliny.wydzial != wydzial:
                self.add_error('rada_dyscypliny', "Wybrana Rada Dyscypliny nie należy do wybranego Wydziału.")
        elif wydzial and not rada_dyscypliny and self.fields['rada_dyscypliny'].required:
             self.add_error('rada_dyscypliny', "Proszę wybrać Radę Dyscypliny dla wybranego Wydziału.")
        elif not wydzial and self.fields['wydzial'].required:
            self.add_error('wydzial', "To pole jest wymagane.")
            
        return cleaned_data
