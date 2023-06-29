from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

# Connection details
db_host = 'localhost'
db_port = '5432'
db_name = 'mydb'
db_user = 'postgres'
db_password = 'password'

# Create the connection string
connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Create the SQLAlchemy engine and session
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()


# Define the SQLAlchemy base class
class Base(DeclarativeBase):
    pass
