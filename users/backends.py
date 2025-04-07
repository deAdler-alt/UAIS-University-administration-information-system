# users/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q # Do tworzenia złożonych zapytań

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # W argumencie 'username' tak naprawdę przyjdzie email z formularza
        # (bo tak nazywa się pole w AuthenticationForm)
        if username is None:
            # Jeśli używamy własnego formularza, który wysyła 'email' zamiast 'username'
            # username = kwargs.get('email')
            # Ale standardowy LoginView wysyła 'username', więc trzymamy się tego.
             username = kwargs.get(UserModel.USERNAME_FIELD)


        try:
            # Szukamy użytkownika po emailu (ignorując wielkość liter)
            # Lub po username (jeśli chcielibyśmy zachować obie opcje)
            # user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))

            # Szukamy TYLKO po emailu
            user = UserModel.objects.get(email__iexact=username)

        except UserModel.DoesNotExist:
            # Zwracamy None, jeśli użytkownik nie istnieje (zgodnie z interfejsem authenticate)
            # Możemy też dodać opóźnienie, aby utrudnić ataki brute-force
            UserModel().set_password(password) # Fałszywe sprawdzenie hasła, aby czas był podobny
            return None
        except UserModel.MultipleObjectsReturned:
             # Jeśli email nie jest unikalny (co nie powinno się zdarzyć, jeśli model ma unique=True)
             # Można zwrócić None lub zalogować błąd
             return None


        # Sprawdzamy hasło i czy użytkownik jest aktywny
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None # Zwracamy None, jeśli hasło jest niepoprawne lub użytkownik nie może się uwierzytelnić

    # Metoda get_user jest dziedziczona z ModelBackend i powinna działać bez zmian
    # def get_user(self, user_id):
    #     try:
    #         return UserModel.objects.get(pk=user_id)
    #     except UserModel.DoesNotExist:
    #         return None