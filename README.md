# Plateforme de services

Application Web réalisée dans le cadre du cours INF6150 à l’UQAM. Elle permet de publier et rechercher des services, de présenter une candidature et d’échanger avec les autres utilisateurs.

## Fonctionnalités

- Inscription, connexion et modification du profil.
- Publication, modification et gestion des offres de services.
- Recherche par mot-clé, catégorie et budget maximal.
- Envoi et traitement des candidatures.
- Favoris, avis et notes.
- Messagerie avec actualisation par WebSocket.

## Technologies

| Partie | Technologies |
| --- | --- |
| Interface | Vue 3, Vue Router, Tailwind CSS, Vite |
| API | Python, FastAPI, Pydantic |
| Données | SQLite, SQLAlchemy |
| Authentification | JWT, bcrypt |
| Tests | pytest, HTTPX |

Le dossier `frontend/` contient l’interface. `backend/app/` regroupe les routes, modèles, schémas de validation et services. Les tests sont dans `backend/tests/`.

## Installation locale sur Windows

Prérequis : Python 3.10 ou plus récent, Node.js 22.12 ou plus récent et npm.

### Backend

Ouvrir PowerShell à la racine du projet :

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Dans `.env`, remplacer la valeur de `JWT_SECRET_KEY` par une clé générée avec :

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Lancer l’API depuis le dossier `backend/` :

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

La base SQLite et les catégories initiales sont créées automatiquement au démarrage. La documentation interactive est accessible à [localhost:8000/docs](http://localhost:8000/docs).

### Frontend

Dans un second terminal, depuis la racine du projet :

```powershell
cd frontend
Copy-Item .env.example .env
npm ci
npm run dev
```

Ouvrir [localhost:5173](http://localhost:5173). Le frontend utilise `VITE_API_URL` pour joindre l’API. Garder le port 5173 pour la configuration CORS fournie.

### Démonstration

Créer un compte et publier un service. Avec un second compte, rechercher ce service, l’ajouter aux favoris, envoyer une candidature et démarrer une conversation. Revenir au premier compte pour consulter les messages et traiter la candidature.

## Vérifications

Depuis `backend/` :

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Depuis `frontend/` :

```powershell
npm run build
```

Sur macOS ou Linux, utiliser `python3` pour créer l’environnement et `.venv/bin/python` pour les commandes Python. Le `Makefile` fournit aussi `make install`, `make backend`, `make frontend`, `make test` et `make build`.

## Configuration

Les fichiers `.env.example` servent de modèles. Conserver les fichiers `.env`, les bases locales et les dossiers de dépendances hors du dépôt. La configuration fournie est destinée au développement local.
