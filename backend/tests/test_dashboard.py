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
    from app.models import User, Category, Service, Candidature

    proprietaire = User(
        id="owner-uuid",
        nom="Dupont",
        prenom="Jean",
        courriel="jean.dupont@example.com",
        date_naissance=date(1990, 1, 1),
        mot_de_passe_hash=get_password_hash("password123"),
        statut=1,
    )
    candidat = User(
        id="candidat-uuid",
        nom="Martin",
        prenom="Julie",
        courriel="julie.martin@example.com",
        date_naissance=date(1992, 5, 5),
        mot_de_passe_hash=get_password_hash("password123"),
        statut=1,
    )
    db.add_all([proprietaire, candidat])

    db.add(Category(id=1, nom="Bricolage", description="Bricolage & Rénovation"))

    service = Service(
        id="service-uuid",
        id_utilisateur="owner-uuid",
        id_categorie=1,
        titre="Montage de meuble",
        description="Assemblage rapide.",
        budget_estime=50.00,
        lieu="Montréal",
        statut="actif",
    )
    db.add(service)

    db.add(
        Candidature(
            id="cand-uuid",
            id_service="service-uuid",
            id_candidat="candidat-uuid",
            message="Je suis disponible cette semaine.",
        )
    )

    db.commit()
    db.close()

    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def candidat_headers():
    token = create_access_token(data={"sub": "julie.martin@example.com", "id": "candidat-uuid"})
    return {"Authorization": f"Bearer {token}"}


def test_mes_candidatures_sans_token():
    response = client.get("/api/candidatures/me")
    assert response.status_code == 401


def test_mes_candidatures_liste(candidat_headers):
    response = client.get("/api/candidatures/me", headers=candidat_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id_service"] == "service-uuid"
    assert data[0]["service_titre"] == "Montage de meuble"
    assert data[0]["service_statut"] == "actif"
    assert data[0]["statut"] == "en_attente"


def test_mes_candidatures_vide_pour_autre_utilisateur():
    """Le propriétaire n'a envoyé aucune candidature : sa liste est vide."""
    owner_token = create_access_token(data={"sub": "jean.dupont@example.com", "id": "owner-uuid"})
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    response = client.get("/api/candidatures/me", headers=owner_headers)
    assert response.status_code == 200
    assert response.json() == []
