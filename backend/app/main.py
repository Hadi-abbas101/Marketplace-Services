from contextlib import asynccontextmanager
from fastapi import FastAPI
from .core.config import ENV
from .db.database import Base, engine, SessionLocal
from .middleware import configure_cors
from .routes import (
    users_router,
    services_router,
    categories_router,
    candidatures_router,
    favoris_router,
    messages_router,
    avis_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialiser les tables de la base de données au démarrage (si elles n'existent pas)
    Base.metadata.create_all(bind=engine)
    
    # Seeding automatique des catégories
    db = SessionLocal()
    try:
        from .models.category import Category
        if db.query(Category).count() == 0:
            default_categories = [
                Category(nom="Maison", description="Services liés à la maison"),
                Category(nom="Informatique", description="Services informatiques et techniques"),
                Category(nom="Création", description="Services créatifs"),
                Category(nom="Marketing", description="Services de marketing"),
                Category(nom="Rédaction", description="Services de rédaction"),
                Category(nom="Administration", description="Services administratifs"),
            ]
            db.add_all(default_categories)
            db.commit()
            print("Catégories initiales insérées avec succès !")
    except Exception as e:
        print(f"Erreur d'initialisation des catégories : {e}")
    finally:
        db.close()
        
    yield

app = FastAPI(
    title="INF6150 - API de Gestion de Projet",
    description="Backend FastAPI pour la gestion des utilisateurs et services",
    version="1.0.0",
    debug=ENV == "development",
    redoc_url=None,
    lifespan=lifespan,
)

configure_cors(app)
app.include_router(users_router)
app.include_router(services_router)
app.include_router(categories_router)
app.include_router(candidatures_router)
app.include_router(favoris_router)
app.include_router(messages_router)
app.include_router(avis_router)
