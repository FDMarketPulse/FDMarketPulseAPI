from sqlalchemy import Column, Float, String, BigInteger, Date
import uuid

from sqlalchemy import Column, String, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from application.infra.models._base import Base


__all__ = ["Cafe", "Employee"]


class Cafe(Base):
    __tablename__ = 'cafe'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(100), nullable=False)
    logo = Column(String(100))
    location = Column(String(100), nullable=False)
    employees = relationship('Employee', backref='cafe', uselist=False)

    # Add the following line to allow redefining the table
    __table_args__ = {'extend_existing': True}


class Employee(Base):
    __tablename__ = 'employee'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email_address = Column(String(100), nullable=False, unique=True)
    phone_number = Column(String(8), nullable=False)
    gender = Column(String(10), nullable=False)
    start_date = Column(Date, nullable=False)
    cafe_id = Column(UUID(as_uuid=True), ForeignKey('cafe.id'))

    # Add the following line to allow redefining the table
    __table_args__ = {'extend_existing': True}
