import pandas as pd
from fastapi import Depends

from application.infra.repository import YfFinMacroRepo


class YfMacroAnalysis:
    """
    Yf Macro Analysis
    """

    def __init__(self, macro_repo: YfFinMacroRepo = Depends()):
        self.macro_repo = macro_repo

    def get_all_macro_data(self):
        query = self.macro_repo.get_overall_macro_data()
        df = pd.read_sql(query.statement, query.session.bind)
        return df.to_json(orient="index")
