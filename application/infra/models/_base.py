import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

__all__ = ["get_db", "Base"]
# Connection details
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

load_dotenv()

connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

engine = create_engine(connection_string)
Base = declarative_base()
SessionLocal = sessionmaker(engine, autoflush=False)


async def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
