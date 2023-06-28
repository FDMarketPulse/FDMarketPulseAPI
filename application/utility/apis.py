from typing import Any

import requests
from fastapi import HTTPException, status
from requests import Response

__all__ = ['Request']


class Request:
    @classmethod
    def get(cls, url: str, params: Any = None, **kwargs: Any):
        return cls._call(requests.get, url, params, **kwargs)

    @classmethod
    def post(cls, url: str, data: Any = None, json: dict = None, **kwargs):
        return cls._call(requests.post, url, data=data, json=json, **kwargs)

    @classmethod
    def put(cls, url: str, data: Any = None, **kwargs):
        return cls._call(requests.put, url, data=data, **kwargs)

    @classmethod
    def delete(cls, url, **kwargs):
        return cls._call(requests.delete, url, **kwargs)

    @classmethod
    def _call(cls, method, url, *args, **kwargs) -> Response:
        kwargs['headers'] = cls._generate_headers(kwargs.get('headers', None))

        try:
            return method(url, *args, **kwargs)
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='. '.join(e.args))

    @staticmethod
    def _generate_headers(headers: dict = None) -> dict:
        default_header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        }

        if headers:
            default_header = {
                **default_header,
                **headers
            }

        return default_header
