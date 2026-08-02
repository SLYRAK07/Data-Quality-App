from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Connexion à un fichier SQLite local (créé automatiquement)
engine = create_engine("sqlite:///./quality.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class AnalysisRun(Base):
    """Une ligne = une analyse de CSV effectuée."""
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    missing_count = Column(Integer)
    outlier_count = Column(Integer)
    duplicate_count = Column(Integer)


# Crée la table si elle n'existe pas encore
Base.metadata.create_all(engine)