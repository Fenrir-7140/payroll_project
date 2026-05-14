import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv() # Charge les variables du fichier .env

# Format : postgresql://utilisateur:mot_de_passe@hôte:port/nom_db
# Exemple : postgresql://admin:mon_code_secret@localhost:5432/payroll_db
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()