import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token

SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Créer les données initiales de test (Utilisateur, Catégorie, Service)
    db = TestingSessionLocal()
    from app.models import User, Category, Service

    # Utilisateur test modular (Martin Julie)
    test_user_modular = User(
        id="user-id-test-123",
        nom="Martin",
        prenom="Julie",
        courriel="julie.martin@example.com",
        date_naissance=date(1995, 10, 10),
        mot_de_passe_hash=get_password_hash("securepwd123"),
        statut=1,
    )
    db.add(test_user_modular)

    # Utilisateur test original (Dupont Jean)
    test_user_original = User(
        id="test-user-uuid",
        nom="Dupont",
        prenom="Jean",
        courriel="jean.dupont@example.com",
        date_naissance=date(1990, 1, 1),
        mot_de_passe_hash=get_password_hash("password123"),
        statut=1,
    )
    db.add(test_user_original)

    # Catégories de test
    cat1 = Category(id=1, nom="Bricolage & Rénovation", description="Services de réparation et travaux manuels")
    cat2 = Category(id=2, nom="Jardinage", description="Jardinage & Extérieur")
    db.add(cat1)
    db.add(cat2)

    db.commit()

    test_service = Service(
        id="service-id-test-456",
        id_utilisateur="user-id-test-123",
        id_categorie=1,
        titre="Peinture de salon",
        description="Je cherche quelqu'un pour peindre mon salon.",
        budget_estime=150.00,
        lieu="Montréal",
        statut="actif",
    )
    db.add(test_service)
    db.commit()
    db.close()
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "jean.dupont@example.com", "id": "test-user-uuid"})
    return {"Authorization": f"Bearer {token}"}


def test_get_service_detail_success():
    """Vérifie que la récupération des détails d'un service existant fonctionne."""
    response = client.get("/api/services/service-id-test-456")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "service-id-test-456"
    assert data["titre"] == "Peinture de salon"
    assert data["description"] == "Je cherche quelqu'un pour peindre mon salon."
    assert data["budget_estime"] == 150.00
    assert data["lieu"] == "Montréal"
    assert data["utilisateur_nom"] == "Martin"
    assert data["utilisateur_prenom"] == "Julie"
    assert data["categorie_nom"] == "Bricolage & Rénovation"


def test_get_service_detail_not_found():
    """Vérifie qu'un service inexistant retourne 404."""
    response = client.get("/api/services/id-inexistant")
    assert response.status_code == 404
    assert response.json()["detail"] == "Le service spécifié n'existe pas."


def test_get_categories():
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nom"] == "Bricolage & Rénovation"
    assert data[1]["nom"] == "Jardinage"


def test_create_service_success(auth_headers):
    payload = {
        "id_categorie": 1,
        "titre": "Réparation de vélo",
        "description": "Je répare votre vélo à domicile",
        "budget_estime": 25.50,
        "lieu": "Montréal, QC",
    }
    response = client.post("/api/services", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["titre"] == "Réparation de vélo"
    assert data["id_utilisateur"] == "test-user-uuid"
    assert data["id_categorie"] == 1
    assert data["budget_estime"] == 25.50
    assert data["lieu"] == "Montréal, QC"
    assert data["statut"] == "actif"
    assert "id" in data


def test_create_service_unauthenticated():
    payload = {
        "id_categorie": 1,
        "titre": "Réparation de vélo",
        "description": "Je répare votre vélo à domicile",
        "budget_estime": 25.50,
        "lieu": "Montréal, QC",
    }
    response = client.post("/api/services", json=payload)
    assert response.status_code == 401


def test_create_service_negative_budget(auth_headers):
    payload = {
        "id_categorie": 1,
        "titre": "Réparation de vélo",
        "description": "Je répare votre vélo à domicile",
        "budget_estime": -10.00,
        "lieu": "Montréal, QC",
    }
    response = client.post("/api/services", json=payload, headers=auth_headers)
    assert response.status_code == 422  # Schema validation fails


def test_create_service_moderation_fail(auth_headers):
    payload = {
        "id_categorie": 1,
        "titre": "Vente d'arme illégale",
        "description": "Je vends des objets de violence",
        "budget_estime": 100.00,
        "lieu": "Montréal, QC",
    }
    response = client.post("/api/services", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Contenu refusé"


def test_get_service_detail_after_create(auth_headers):
    # D'abord créer un service
    payload = {
        "id_categorie": 1,
        "titre": "Réparation de vélo",
        "description": "Je répare votre vélo à domicile",
        "budget_estime": 25.50,
        "lieu": "Montréal, QC",
    }
    create_res = client.post("/api/services", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    service_id = create_res.json()["id"]

    # Ensuite récupérer les détails
    response = client.get(f"/api/services/{service_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == service_id
    assert data["utilisateur_nom"] == "Dupont"
    assert data["utilisateur_prenom"] == "Jean"
    assert data["categorie_nom"] == "Bricolage & Rénovation"
    assert data["titre"] == "Réparation de vélo"
    assert data["budget_estime"] == 25.50
    assert data["lieu"] == "Montréal, QC"

