from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./events.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer,autoincrement=True, primary_key=True, index=True)
    event_id = Column(String, unique=True)
    coefficient = Column(Float, nullable=False)
    deadline = Column(Integer, nullable=False)
    state = Column(Integer, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)
