import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash

SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_search_db():
    app.dependency_overrides[get_db] = _override_get_db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    from app.models import User, Category, Service

    user = User(
        id="search-user-1",
        nom="Tremblay",
        prenom="Alice",
        courriel="alice@example.com",
        date_naissance=date(1995, 5, 5),
        mot_de_passe_hash=get_password_hash("password123"),
        statut=1,
    )
    db.add(user)

    category = Category(id=1, nom="Bricolage", description="Travaux")
    db.add(category)

    db.add(
        Service(
            id="svc-actif-peinture",
            id_utilisateur="search-user-1",
            id_categorie=1,
            titre="Peinture de salon",
            description="Service de peinture intérieure",
            budget_estime=200,
            lieu="Montréal",
            statut="actif",
        )
    )
    db.add(
        Service(
            id="svc-inactif-peinture",
            id_utilisateur="search-user-1",
            id_categorie=1,
            titre="Peinture de garage",
            description="Offre retirée",
            budget_estime=100,
            lieu="Laval",
            statut="inactif",
        )
    )
    db.commit()
    db.close()
    yield
    app.dependency_overrides.pop(get_db, None)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_search_services_by_title():
    response = client.get("/api/services", params={"mot_cle": "Peinture"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "svc-actif-peinture"
    assert data[0]["titre"] == "Peinture de salon"


def test_search_services_by_description_and_exclude_inactive():
    response = client.get("/api/services", params={"mot_cle": "intérieure"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "svc-actif-peinture"

    inactive = client.get("/api/services", params={"mot_cle": "garage"})
    assert inactive.status_code == 200
    assert inactive.json() == []


def test_search_services_case_and_accent_insensitive():
    by_case = client.get("/api/services", params={"mot_cle": "peinture"})
    assert by_case.status_code == 200
    assert len(by_case.json()) == 1

    by_accent = client.get("/api/services", params={"mot_cle": "interieure"})
    assert by_accent.status_code == 200
    assert len(by_accent.json()) == 1
    assert by_accent.json()[0]["id"] == "svc-actif-peinture"


def test_search_services_empty_keyword_returns_all_active():
    response = client.get("/api/services", params={"mot_cle": ""})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["statut"] == "actif"


def test_search_services_no_results():
    response = client.get("/api/services", params={"mot_cle": "introuvable-xyz"})
    assert response.status_code == 200
    assert response.json() == []


def test_search_services_mot_cle_max_length():
    response = client.get("/api/services", params={"mot_cle": "a" * 101})
    assert response.status_code == 422


def test_search_services_without_authentication():
    response = client.get("/api/services", params={"mot_cle": "Peinture"})
    assert response.status_code == 200
    assert len(response.json()) == 1
