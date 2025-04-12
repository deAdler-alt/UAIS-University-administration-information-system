# UAIS - University Administration Information System

System informatyczny administracji uniwersyteckiej (UAIS) to aplikacja webowa oparta na Django, która umożliwia zarządzanie użytkownikami, rolami oraz innymi funkcjami administracyjnymi.

---

## Jak uruchomić projekt?

### 1. Klonowanie repozytorium

Najpierw sklonuj repozytorium na swój lokalny komputer:

```bash
git clone <URL_REPOZYTORIUM>
cd UAIS-University-administration-information-system
```

---

### 2. Utworzenie i aktywacja wirtualnego środowiska

Utwórz wirtualne środowisko Python w folderze `.venv`:

```bash
python3 -m venv .venv
```

Aktywuj wirtualne środowisko:

```bash
source .venv/bin/activate
```

---

### 3. Instalacja zależności

Zainstaluj wymagane pakiety z pliku `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 4. Migracje bazy danych

Utwórz bazę danych SQLite i zastosuj migracje:

```bash
python manage.py migrate
```

---

### 5. Docker

Uruchom projekt w kontenerze Docker:

1. Zbuduj obraz:

   ```bash
   docker-compose build
   ```

2. Uruchom kontener:

   ```bash
   docker-compose up
   ```

Serwer będzie dostępny pod adresem: [http://127.0.0.1:8000](http://127.0.0.1:8000)

**Uwaga dla użytkowników Linuxa z włączonym SELinux:**

Jeśli używasz SELinux i masz problemy z dostępem do wolumenów, musisz zmienić kontekst bezpieczeństwa dla katalogu z wolumenami. Użyj poniższego polecenia, aby to zrobić:

```bash
chcon -Rt svirt_sandbox_file_t /path/to/volume
```

Zastąp `/path/to/volume` ścieżką do katalogu, który jest montowany jako wolumen w kontenerze.

---

### 5.1 Uruchomienie serwera deweloperskiego (Alternatywa)

Jeśli chcesz uruchomić serwer lokalny:

```bash
python manage.py runserver
```

Serwer będzie dostępny pod adresem: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 6. Logowanie do panelu administracyjnego

Aby uzyskać dostęp do panelu administracyjnego, możesz utworzyć superużytkownika:

```bash
python manage.py createsuperuser
```

**Lub możesz użyć istniejących danych logowania:**

- **Email:** <Admin1@edu.pl>  
  **Hasło:** Administrator@123  

- **Email:** <admin@edu.pl>  
  **Hasło:** passwordadmin

Następnie zaloguj się na jeden z tych adresów:

- [http://127.0.0.1:8000/accounts/login](http://127.0.0.1:8000/accounts/login) (Normal login)
- [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) (Django admin)

---

## Struktura projektu

- **`users/`**: Obsługa użytkowników (logowanie, role, modele).
- **`management/`**: Zarządzanie użytkownikami i innymi zasobami.
- **`templates/`**: Szablony HTML dla aplikacji.
- **`uais_config/`**: Konfiguracja projektu Django.

---

## Wymagania systemowe

- Python 3.11+
- Django 5.2
- SQLite (domyślna baza danych)

---

## Autorzy

- [GitEagly](https://github.com/GitEagly)
- [FiFulini](https://github.com/FiFulini)
- [NixyFox](https://github.com/rasto50)

---
