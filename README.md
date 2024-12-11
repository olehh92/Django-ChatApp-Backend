# Django-Projekt: DABubble

DABubble ist ein Projekt zur Verwaltung und Kommunikation in Channels. Es wurde mit dem Django-Webframework entwickelt. Das Frontend ist über Angular zugänglich unter folgendem Link:

https://github.com/TimWidl94/DaBubble-Frontend

## Funktionen
- Benutzerregistrierung und -authentifizierung
- Erstellen und Verwalten von Channels
- Nachrichten in Channels posten
- Erstellen eines Threads
- Reaktionen per Emojis
- Datenspeicherung über das Hochladen von Dateien im privaten Channel
- Admin-Oberfläche zur Verwaltung

## Voraussetzungen
Bevor Sie das Projekt starten, stellen Sie sicher, dass folgende Software installiert ist:
- Python 3.8 oder höher
- Django 4.0 oder höher
- Ein Datenbankmanagementsystem (z. B. SQLite, PostgreSQL)

## Installation

### 1. Repository klonen

git clone https://github.com/TimWidl94/Django-ChatApp-Backend/tree/main
cd DABubble_Backend

### 2. Virtuelle Umgebung erstellen

python -m venv venv
source venv/bin/activate  # Auf Windows: venv\Scripts\activate


### 3. Abhängigkeiten installieren

pip install -r requirements.txt

### 4. .env-Datei erstellen

Beispiel:

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=IhrEmail@example.com
EMAIL_HOST_PASSWORD=IhrPasswort
DEFAULT_FROM_EMAIL=DABubble@example.com

### 5. Datenbank migrieren

python manage.py migrate

### 6. Server starten

python manage.py runserver


Nutzung:
Rufen Sie die lokale Entwicklungsumgebung unter http://127.0.0.1:8000/ auf.
Melden Sie sich an oder registrieren Sie sich, um das System zu verwenden.

Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe LICENSE für weitere Informationen.

Autor

Tim Widl https://github.com/TimWidl94