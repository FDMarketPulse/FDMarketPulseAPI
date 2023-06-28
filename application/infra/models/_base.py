from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

__all__ = ["get_db", "Base"]
# Connection details
db_host = 'localhost'
db_port = '5433'
db_name = 'postgres'
db_user = 'postgres'
db_password = 'postgres'

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
