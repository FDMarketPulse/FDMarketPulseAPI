from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

__all__ = ["get_db", "Base"]
# Connection details
db_host = 'localhost'
db_port = '5432'
db_name = 'mydb'
db_user = 'postgres'
db_password = 'password'

connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
connection_string = "postgresql://doadmin:AVNS_vhMPBp3xk2iVcK-mogM@db-postgresql-nyc1-95738-do-user-14221760-0.b.db.ondigitalocean.com:25060/defaultdb"

engine = create_engine(connection_string)
Base = declarative_base()
SessionLocal = sessionmaker(engine, autoflush=False)


async def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
