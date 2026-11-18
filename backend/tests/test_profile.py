import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash

# SQLite en mémoire pour tester
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
    
    # Créer un utilisateur de test
    db = TestingSessionLocal()
    from app.models import User
    test_user = User(
        nom="Martin",
        prenom="Julie",
        courriel="julie.martin@example.com",
        date_naissance=date(1995, 10, 10),
        mot_de_passe_hash=get_password_hash("securepwd123"),
        statut=1
    )
    db.add(test_user)
    db.commit()
    db.close()
    yield
    app.dependency_overrides.pop(get_db, None)

def test_get_profile_success():
    """Vérifie que la récupération du profil connecté fonctionne avec un token valide."""
    # 1. Se connecter pour récupérer un jeton
    login_payload = {
        "courriel": "julie.martin@example.com",
        "mot_de_passe": "securepwd123"
    }
    login_response = client.post("/api/users/login", json=login_payload)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 2. Utiliser le jeton pour obtenir le profil
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["courriel"] == "julie.martin@example.com"
    assert data["nom"] == "Martin"
    assert data["prenom"] == "Julie"
    assert "services" in data
    assert len(data["services"]) == 0

def test_get_profile_no_token():
    """Vérifie que l'accès au profil sans jeton renvoie 401."""
    response = client.get("/api/users/me")
    assert response.status_code == 401

def test_get_profile_invalid_token():
    """Vérifie que l'accès au profil avec un jeton invalide renvoie 401."""
    headers = {"Authorization": "Bearer mauvais_token_jwt"}
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 401
