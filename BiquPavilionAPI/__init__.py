import demjson

from BiquPavilionAPI import HttpUtil


def get(api_url: str, params: dict = None) -> [str, dict]:
    response = HttpUtil.get(api_url, params)
    if response:
        return demjson.decode(str(response.text))
    print('[ERROR]', api_url)


class Book:

    @staticmethod
    def novel_info(novel_id: str):
        response = get("https://infosxs.pysmei.com/BookFiles/Html/{}/info.html".format(novel_id))
        if response is not None and response.get('info') == 'success':
            return response.get('data')

    @staticmethod
    def catalogue(novel_id):
        novel_id = str(int(int(novel_id) / 1000) + 1) + "/" + str(novel_id)
        response = get("https://infosxs.pysmei.com/BookFiles/Html/{}/index.html".format(novel_id))
        if response is not None and response.get('info') == 'success':
            return response.get('data').get('list')

    @staticmethod
    def search(key: str, page: int = 1):
        params = {"key": key, "page": page, "siteid": "app2"}
        response = get("https://souxs.leeyegy.com/search.aspx", params=params)
        if response is not None and response.get('info') == 'success':
            return response.get('data')


class Chapter:
    @staticmethod
    def content(novel_id, chapter_id: str):
        book_id = str(int(int(novel_id) / 1000) + 1) + "/" + str(novel_id)
        response = get("https://contentxs.pysmei.com/BookFiles/Html/{}/{}.html".format(book_id, chapter_id))
        if response is not None and response.get('info') == 'success':
            return response.get('data')


class Cover:
    @staticmethod
    def download_cover(url: str, params: dict = None) -> bytes:
        response = HttpUtil.get(url, params=params)
        if response:
            return response.content
        print('[ERROR COVER]', url)
