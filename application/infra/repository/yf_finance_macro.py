from fastapi import Depends
from sqlalchemy.orm import Session

from application.infra import Macro
from application.infra.models._base import get_db

__all__ = ['YfFinMacroRepo']


class YfFinMacroRepo:
    """
    Yahoo Finance Macro Data From DB
    """

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_overall_macro_data(self):
        item = self.db.query(Macro)
        # self.db.close()

        return item
