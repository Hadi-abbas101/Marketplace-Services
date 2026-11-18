import os
import secrets

from dotenv import load_dotenv


load_dotenv()

ENV = os.getenv("ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
