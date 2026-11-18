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


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_filter_db():
    app.dependency_overrides[get_db] = _override_get_db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    from app.models import User, Category, Service

    db.add(
        User(
            id="filter-user-1",
            nom="Roy",
            prenom="Sam",
            courriel="sam@example.com",
            date_naissance=date(1992, 3, 3),
            mot_de_passe_hash=get_password_hash("password123"),
            statut=1,
        )
    )
    db.add(Category(id=1, nom="Bricolage", description="Travaux"))
    db.add(Category(id=2, nom="Jardinage", description="Vert"))

    db.add(
        Service(
            id="svc-bricolage-200",
            id_utilisateur="filter-user-1",
            id_categorie=1,
            titre="Peinture salon",
            description="Peinture intérieure",
            budget_estime=200,
            lieu="Montréal",
            statut="actif",
        )
    )
    db.add(
        Service(
            id="svc-jardinage-80",
            id_utilisateur="filter-user-1",
            id_categorie=2,
            titre="Tonte pelouse",
            description="Entretien gazon",
            budget_estime=80,
            lieu="Laval",
            statut="actif",
        )
    )
    db.add(
        Service(
            id="svc-bricolage-inactif",
            id_utilisateur="filter-user-1",
            id_categorie=1,
            titre="Service retiré",
            description="Inactif",
            budget_estime=50,
            lieu="Montréal",
            statut="inactif",
        )
    )
    db.commit()
    db.close()
    yield
    app.dependency_overrides.pop(get_db, None)


def test_filter_services_by_category():
    response = client.get("/api/services", params={"mot_cle": "", "id_categorie": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "svc-bricolage-200"


def test_filter_services_by_budget_max():
    response = client.get("/api/services", params={"mot_cle": "", "budget_max": 100})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "svc-jardinage-80"


def test_filter_services_combine_keyword_category_and_budget():
    response = client.get(
        "/api/services",
        params={"mot_cle": "Peinture", "id_categorie": 1, "budget_max": 250},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "svc-bricolage-200"

    empty = client.get(
        "/api/services",
        params={"mot_cle": "Peinture", "id_categorie": 2, "budget_max": 250},
    )
    assert empty.status_code == 200
    assert empty.json() == []


def test_filter_services_reject_negative_budget_and_unknown_category():
    negative = client.get("/api/services", params={"mot_cle": "", "budget_max": -1})
    assert negative.status_code == 422

    unknown = client.get("/api/services", params={"mot_cle": "", "id_categorie": 999})
    assert unknown.status_code == 400
    assert unknown.json()["detail"] == "La catégorie spécifiée n'existe pas."
