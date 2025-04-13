# users/forms.py
from django import forms

class PinVerificationForm(forms.Form):
    pin = forms.CharField(
        label='Kod PIN',
        max_length=4,
        min_length=4,
        # Atrybuty HTML5 ułatwiające wpisywanie cyfr na urządzeniach mobilnych
        # i potencjalne autouzupełnianie kodu z SMS/email
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'autocomplete': 'one-time-code',
            'class': 'form-control form-control-lg text-center pin-input' # Dodajemy klasy dla stylów
        }),
        help_text='Wpisz 4-cyfrowy kod PIN otrzymany w wiadomości email.'
    )

    def clean_pin(self):
        pin = self.cleaned_data.get('pin')
        if not pin.isdigit():
            raise forms.ValidationError("Kod PIN może zawierać tylko cyfry.")
        if len(pin) != 4: # Dodatkowe sprawdzenie długości
             raise forms.ValidationError("Kod PIN musi składać się z 4 cyfr.")
        return pin