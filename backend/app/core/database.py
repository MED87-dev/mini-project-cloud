"""
Configuration de la connexion à la base de données PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Créer le moteur SQLAlchemy avec gestion d'erreurs améliorée
# Note: create_engine ne se connecte pas immédiatement, donc cela ne devrait pas échouer
# même si PostgreSQL n'est pas disponible
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Vérifie la connexion avant utilisation
    pool_size=10,
    max_overflow=20,
    echo=False,  # Mettre à True pour voir les requêtes SQL
    connect_args={
        "connect_timeout": 10,  # Timeout de connexion de 10 secondes
    }
)
logger.info(f"✅ Moteur SQLAlchemy créé avec succès")

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """
    Dépendance pour obtenir une session de base de données
    """
    from sqlalchemy import text
    from fastapi import HTTPException, status
    
    db = SessionLocal()
    try:
        # Tester la connexion avant de retourner la session
        db.execute(text("SELECT 1"))
        yield db
    except SQLAlchemyError as e:
        logger.error(f"❌ Erreur de connexion à la base de données: {e}")
        db.rollback()
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "connection refused" in error_msg or "connection timed out" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Impossible de se connecter à PostgreSQL. Vérifiez que le serveur est démarré et que la base de données existe."
            )
        elif "relation" in error_msg and "does not exist" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Les tables de la base de données n'existent pas. Veuillez initialiser la base de données."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Erreur de base de données: {str(e)}"
            )
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue: {str(e)}"
        )
    finally:
        db.close()

