from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

__all__ = ["get_db", "Base"]
# Connection details
# db_host = 'localhost'
# db_port = '5432'
# db_name = 'mydb'
# db_user = 'postgres'
# db_password = 'password'

# connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
connection_string = "postgresql://defaultdb_xdbr_user:QsKsnZrlAGWRpVIgBo1l3DTwziiAKpXl@dpg-ck5dum6ru70s73c6f5i0-a" \
                    ".singapore-postgres.render.com/defaultdb_xdbr"

engine = create_engine(connection_string)
Base = declarative_base()
SessionLocal = sessionmaker(engine, autoflush=False)


async def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
