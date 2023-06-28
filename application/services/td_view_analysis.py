import snakecase

from application.utility import Request


class TdViewAnalysis:
    """
    Trading View Website APIs
    """

    def __init__(self):
        self.cookies = {}
        self.headers = {}
        self.columns = ["description", "market", "change", "Perf.W", "Perf.1M", "Perf.3M", "Perf.6M", "Perf.YTD",
                        "Perf.Y", "Perf.5Y", "Perf.All"]
        self.type = "sector"
        self.data = {
            "columns": self.columns, "filter": [{"left": "description", "operation": "nempty"}],
            "ignore_unknown_fields": False, "options": {"lang": "en"}, "range": [0, 1000],
            "sort": {"sortBy": "description", "sortOrder": "asc"},
            "symbols": {"query": {"types": [self.type]}, "tickers": []}, "markets": ["america"]}



    def get_overall_ind_sec_data(self):
        result = []
        for i in ["sector", "industry"]:
            result.append({"type": i, "value": self.get_industry_sector_data(value_type=i)})
        return result

    def get_industry_sector_data(self, value_type: str, url: str = "https://scanner.tradingview.com/america/scan",
                                 ):
        """
        :param
        url: url of the request
        value_type: sector or industry
        :return:
        """
        response = Request.post(url, cookies=self.cookies, headers=self.headers,
                                json=self.json_data(value_type))
        list_result = []
        for i in response.json()['data']:
            temp_dict = {}
            for e, c in zip(i['d'], self.columns):
                temp_dict[snakecase.convert(c.replace(".", "_"))] = e
            list_result.append(temp_dict)

        return list_result

    def get_sector_data(self, url: str = "https://scanner.tradingview.com/america/scan"):
        """

        :param url: url of the request
        :return:
        """

        response = Request.post(url, cookies=self.cookies, headers=self.headers,
                                json=self.data)
        list_result = []
        for i in response.json()['data']:
            temp_dict = {}
            for e, c in zip(i['d'], self.columns):
                temp_dict[snakecase.convert(c.replace(".", "_"))] = e
            list_result.append(temp_dict)

        return list_result


    def json_data(self, query_type: str):
        return {
            "columns": self.columns, "filter": [{"left": "description", "operation": "nempty"}],
            "ignore_unknown_fields": False, "options": {"lang": "en"}, "range": [0, 1000],
            "sort": {"sortBy": "description", "sortOrder": "asc"},
            "symbols": {"query": {"types": [query_type]}, "tickers": []}, "markets": ["america"]}
