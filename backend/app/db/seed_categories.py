from app.db.database import SessionLocal
from app.models import Category

categories = [
    ("Maison", "Services liés à la maison"),
    ("Informatique", "Services informatiques et techniques"),
    ("Création", "Services créatifs"),
    ("Marketing", "Services de marketing"),
    ("Rédaction", "Services de rédaction"),
    ("Administration", "Services administratifs"),
]

db = SessionLocal()

try:
    for nom, description in categories:
        exists = db.query(Category).filter(Category.nom == nom).first()
        if not exists:
            db.add(Category(nom=nom, description=description))

    db.commit()
    print("Catégories ajoutées.")
finally:
    db.close()