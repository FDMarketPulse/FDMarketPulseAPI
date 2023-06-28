from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

# Connection details
db_host = 'localhost'
db_port = '5431'
db_name = 'postgres'
db_user = 'postgres'
db_password = 'postgres'

# Create the connection string
connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Create the SQLAlchemy engine and session
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()


# Define the SQLAlchemy base class
class Base(DeclarativeBase):
    pass
