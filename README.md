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

### 5. Uruchomienie serwera deweloperskiego

Uruchom serwer lokalny:

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

Następnie zaloguj się pod adresem: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## Dodatkowe informacje

### Docker (opcjonalnie)

Jeśli chcesz uruchomić projekt w kontenerze Docker:

1. Zbuduj obraz:

   ```bash
   docker-compose build
   ```

2. Uruchom kontener:

   ```bash
   docker-compose up
   ```

Serwer będzie dostępny pod adresem: [http://127.0.0.1:8000](http://127.0.0.1:8000)

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
