from application.infra.models._base import Base

from sqlalchemy import Column, Float, String, BigInteger, Date, UniqueConstraint
from sqlalchemy import Column, Float, String, BigInteger, Date, UniqueConstraint

from application.infra.models._base import Base

__all__ = ["Macro"]


class Macro(Base):
    __tablename__ = 'yf_macro'

    id = Column(BigInteger, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    ticker = Column(String)
    adj_close = Column(Float(precision=10))
    close = Column(Float(precision=10))
    high = Column(Float(precision=10))
    low = Column(Float(precision=10))
    open = Column(Float(precision=18))
    volume = Column(BigInteger)
    daily_return = Column(Float(precision=18))

    __table_args__ = (
        UniqueConstraint('date', 'ticker', name='_date_ticker_uc'),
    )