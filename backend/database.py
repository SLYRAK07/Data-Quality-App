from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///./data/quality.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class AnalysisRun(Base):
    """Une ligne = une analyse de CSV effectuee."""
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_rows = Column(Integer)
    missing_count = Column(Integer)
    outlier_count = Column(Integer)
    duplicate_count = Column(Integer)
    quality_score = Column(Float)


class SavedConfig(Base):
    """Une configuration de controles sauvegardee et reutilisable."""
    __tablename__ = "saved_configs"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    range_configs = Column(String)
    ignore_columns = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """Un utilisateur autorise a se connecter a l'application."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)