from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/dbname"

# Создание экземпляра класса Engine для подключения к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание экземпляра класса SessionLocal для управления сессиями базы данных
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


Base = declarative_base()
