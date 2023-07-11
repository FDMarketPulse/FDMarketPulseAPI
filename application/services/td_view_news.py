import re

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

from application.utility import Request


class TdViewNews:
    """
    Trading View Website News APIs
    """

    def __init__(self):
        self.cookies = {}
        self.headers = {}
        self.data = {}

    def get_overall_news(self):
        list_of_new_type = ['base', 'crypto', 'stock', 'forex', 'index', 'futures', 'bond', 'economic']

        news_list = []
        for i in list_of_new_type:
            if i == 'stock':
                params = {
                    'client': 'web',
                    'lang': 'en',
                    'category': i,
                    'market_country': 'US'
                }
            else:
                params = {
                    'client': 'web',
                    'lang': 'en',
                    'category': i,
                }
            response = Request.get('https://news-headlines.tradingview.com/v2/headlines', params=params,
                                   headers=self.headers)
            wanted_keys = ['id', 'title', 'provider', 'published']
            filtered_data = [{key: item[key] for key in item if key in wanted_keys} for item in
                             response.json()['items']]
            sia = SIA()
            results = []
            for line in filtered_data:
                pol_score = sia.polarity_scores(line['title'])
                label = 0
                if pol_score['compound'] > 0.5:
                    label = 1
                elif pol_score['compound'] < -0.2:
                    label = -1
                line['sentiment'] = label
                results.append(line)
            news_list.append({"type": i, 'result': results})

        return news_list

    def _convert_keys_to_snake_case(self, dictionary):
        snake_case_dict = {}
        for key, value in dictionary.items():
            snake_case_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            snake_case_dict[snake_case_key] = value
        return snake_case_dict

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
