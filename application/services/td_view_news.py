import re
from concurrent.futures import ThreadPoolExecutor
from application.utility import Request

class TdViewNews:
    """
    Trading View Website News APIs
    """

    def __init__(self):
        self.cookies = {}
        self.headers = {}

    def _get_news_by_type(self, news_type: str):
        params = {
            'client': 'web',
            'lang': 'en',
            'category': news_type
        }

        if news_type == 'stock':
            params['market_country'] = 'US'

        response = Request.get('https://news-headlines.tradingview.com/v2/headlines', params=params,
                               headers=self.headers)
        wanted_keys = ['id', 'title', 'provider', 'published']
        filtered_data = [{key: item[key] for key in item if key in wanted_keys} for item in
                         response.json()['items']]
        return {"type": news_type, 'result': filtered_data}

    def get_overall_news(self):
        list_of_new_type = ['base', 'crypto', 'stock', 'forex', 'index', 'futures', 'bond', 'economic']
        with ThreadPoolExecutor() as executor:
            news_list = list(executor.map(self._get_news_by_type, list_of_new_type))

        return news_list

    def get_single_news(self, news_id: str):
        params = {
            'id': news_id,
            'lang': 'en'
        }

        response = Request.get('https://news-headlines.tradingview.com/v2/story', params=params, headers=self.headers)

        list_news_string = []
        try:
            for i in response.json()['astDescription']['children']:
                my_list = i['children']
                filtered_list = [item for item in my_list if isinstance(item, str)]
                updated_string = re.sub(r'\s+', ' ', "".join(filtered_list))
                if updated_string != "":
                    list_news_string.append(updated_string)

            return {"summary": response.json()['shortDescription'], 'id': response.json()['id'],
                    'content': list_news_string}
        except Exception as e:
            return {"summary": "", 'id': "",
                    'content': []}
