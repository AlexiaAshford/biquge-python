import requests
import functools
from instance import *

session = requests.Session()

session.headers.update({
    "Connection": "Keep-Alive",
    "Cache-Control": "no-cache",
    "Accept-Encoding": "gzip",
    'User-Agent': "okhttp-okgo/jeasonlzy"
})


class MaxRetry:
    def __init__(self, max_retry):
        self.max_retry = max_retry

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for retry in range(self.max_retry):
                response = func(*args, **kwargs)
                if not isinstance(response, bool):
                    return response
                else:
                    time.sleep(retry * 0.05)

            return False

        return wrapper


def request(method, api_url: str, data=None, params=None, **kwargs):
    for retry in range(5):
        try:
            response = method(api_url, headers=session.headers, params=params, data=data, **kwargs)
            response.encoding = 'utf-8-sig'
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException as error:
            print(f"\n{method.__name__.upper()} url:{api_url} Error:{error}")


def get(api_url: str, params=None, **kwargs) -> requests.Response:
    return request(requests.get, api_url, params=params, **kwargs)


def post(api_url: str, data=None, **kwargs) -> requests.Response:
    return request(requests.post, api_url, data=data, **kwargs)


def put(api_url: str, data=None, **kwargs):
    return request(requests.put, api_url, data=data, **kwargs)
