from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://users:Zoir2002@192.168.3.10:5432"

# Создание экземпляра класса Engine для подключения к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание экземпляра класса SessionLocal для управления сессиями базы данных
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


Base = declarative_base()
