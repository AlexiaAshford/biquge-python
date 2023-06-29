import requests
import functools
from instance import *

session = requests.Session()

session.headers.update({
    "Connection": "Keep-Alive",
    "Cache-Control": "no-cache",
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


def request(method: str, api_url: str, data=None, params=None, **kwargs):
    for retry in range(5):
        try:
            response = requests.request(method, api_url, headers=session.headers, params=params, data=data, **kwargs)
            response.encoding = 'utf-8-sig'
            return response
        except Exception as error:
            print(f"\n{method.upper()} url:{api_url} Error:{error}")


def get(api_url: str, params=None, **kwargs):
    res = request("get", api_url, params=params, **kwargs)
    if res.status_code == 200:
        if api_url.find(".jpg") != -1:
            return res.content
        try:
            return res.json()
        except:
            return res.text
    return {"code": res.status_code, "info": str(res.text)}


def post(api_url: str, data=None, **kwargs) -> requests.Response:
    return request("post", api_url, data=data, **kwargs)


def put(api_url: str, data=None, **kwargs):
    return request("put", api_url, data=data, **kwargs)
