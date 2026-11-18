import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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

    db = TestingSessionLocal()
    from app.models import User, Category, Service

    # Propriétaire du service
    proprietaire = User(
        id="owner-uuid",
        nom="Dupont",
        prenom="Jean",
        courriel="jean.dupont@example.com",
        date_naissance=date(1990, 1, 1),
        mot_de_passe_hash=get_password_hash("password123"),
        statut=1,
    )
    # Utilisateur qui met en favori
    visiteur = User(
        id="visitor-uuid",
        nom="Martin",
        prenom="Julie",
        courriel="julie.martin@example.com",
        date_naissance=date(1992, 5, 5),
        mot_de_passe_hash=get_password_hash("password123"),
        statut=1,
    )
    db.add_all([proprietaire, visiteur])

    categorie = Category(id=1, nom="Bricolage", description="Bricolage & Rénovation")
    db.add(categorie)

    service = Service(
        id="service-uuid",
        id_utilisateur="owner-uuid",
        id_categorie=1,
        titre="Montage de meuble",
        description="Assemblage rapide et soigné.",
        budget_estime=50.00,
        lieu="Montréal",
        statut="actif",
    )
    db.add(service)

    db.commit()
    db.close()

    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "julie.martin@example.com", "id": "visitor-uuid"})
    return {"Authorization": f"Bearer {token}"}


def test_ajouter_favori_success(auth_headers):
    response = client.post("/api/services/service-uuid/favoris", headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["id_service"] == "service-uuid"
    assert data["id_utilisateur"] == "visitor-uuid"


def test_ajouter_favori_sans_token():
    response = client.post("/api/services/service-uuid/favoris")
    assert response.status_code == 401


def test_ajouter_favori_service_inexistant(auth_headers):
    response = client.post("/api/services/inexistant/favoris", headers=auth_headers)
    assert response.status_code == 404


def test_ajouter_favori_doublon(auth_headers):
    client.post("/api/services/service-uuid/favoris", headers=auth_headers)
    response = client.post("/api/services/service-uuid/favoris", headers=auth_headers)
    assert response.status_code == 409


def test_lister_favoris(auth_headers):
    client.post("/api/services/service-uuid/favoris", headers=auth_headers)
    response = client.get("/api/favoris", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id_service"] == "service-uuid"
    assert data[0]["titre"] == "Montage de meuble"
    assert data[0]["categorie_nom"] == "Bricolage"


def test_lister_favoris_vide(auth_headers):
    response = client.get("/api/favoris", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_retirer_favori(auth_headers):
    client.post("/api/services/service-uuid/favoris", headers=auth_headers)
    response = client.delete("/api/services/service-uuid/favoris", headers=auth_headers)
    assert response.status_code == 204

    liste = client.get("/api/favoris", headers=auth_headers)
    assert liste.json() == []


def test_retirer_favori_absent(auth_headers):
    response = client.delete("/api/services/service-uuid/favoris", headers=auth_headers)
    assert response.status_code == 404


def test_favori_disparait_si_service_supprime(auth_headers):
    """Critère d'acceptation : un service supprimé disparaît des favoris."""
    client.post("/api/services/service-uuid/favoris", headers=auth_headers)

    # Le propriétaire supprime son service
    owner_token = create_access_token(data={"sub": "jean.dupont@example.com", "id": "owner-uuid"})
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    suppression = client.delete("/api/services/service-uuid", headers=owner_headers)
    assert suppression.status_code == 204

    # Le favori a disparu
    liste = client.get("/api/favoris", headers=auth_headers)
    assert liste.status_code == 200
    assert liste.json() == []
