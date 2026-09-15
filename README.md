# Code repositories — backend Django

API Django REST (sans front-end) pour gérer des repositories de code, leurs fichiers, la recherche, et le signalement des fichiers critiques.

## Prérequis

- Python 3.11 ou plus récent
- pip

## Installation

```powershell
cd C:\Users\dell\CHallenge
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Sous Linux / macOS :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

L’API est disponible sur `http://127.0.0.1:8000/api/`.
L’admin Django est sur `http://127.0.0.1:8000/admin/` (créer un compte avec `python manage.py createsuperuser` si besoin).

## Tests

```powershell
python manage.py test repositories
```

## Endpoints

| Méthode | URL | Rôle |
| --- | --- | --- |
| POST | `/api/repositories/` | Créer un repository |
| GET | `/api/repositories/` | Lister les repositories |
| GET | `/api/repositories/{id}/` | Détail d’un repository (fichiers inclus) |
| GET | `/api/repositories/{id}/files/` | Lister les fichiers du repository |
| POST | `/api/repositories/{id}/files/` | Ajouter un fichier |
| GET | `/api/files/?name=&language=&type=` | Rechercher des fichiers |
| GET | `/api/files/critical/` | Fichiers considérés comme critiques |

## Exemples de requêtes

Créer un repository :

```bash
curl -X POST http://127.0.0.1:8000/api/repositories/ ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \"billing-api\", \"description\": \"API facturation\", \"owner\": \"ops\"}"
```

Ajouter un fichier :

```bash
curl -X POST http://127.0.0.1:8000/api/repositories/1/files/ ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \".env\", \"path\": \"billing/.env\", \"file_type\": \"config\", \"language\": \"\", \"size_bytes\": 320, \"description\": \"\"}"
```

Rechercher :

```bash
curl "http://127.0.0.1:8000/api/files/?name=env"
curl "http://127.0.0.1:8000/api/files/?language=python"
curl "http://127.0.0.1:8000/api/files/?type=config"
```

Fichiers critiques :

```bash
curl http://127.0.0.1:8000/api/files/critical/
```

Le navigateur browsable de Django REST Framework (`http://127.0.0.1:8000/api/`) permet aussi de tester les endpoints sans client HTTP.

## Fichiers critiques

Un fichier est signalé critique s’il vérifie au moins un critère :

- taille ≥ `CRITICAL_FILE_SIZE_BYTES` (100 000 octets par défaut, dans `config/settings.py`)
- type `config` ou nom/chemin typique de configuration
- type `security` ou nom/chemin typique de secret / clé
- description vide

Les champs calculés `is_critical` et `critical_reasons` sont renvoyés sur chaque fichier.

## Structure

```
config/           # projet Django (settings, urls)
repositories/     # application métier
  models.py
  services.py     # règles fichiers critiques
  views.py
  serializers.py
  filters.py
  tests/
```
