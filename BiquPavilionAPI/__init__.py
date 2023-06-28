import re
import demjson
import base64
from Crypto.Cipher import DES3
from Crypto.Util.Padding import unpad

from BiquPavilionAPI import HttpUtil


def get(api_url: str, params: dict = None) -> [str, dict]:
    response = HttpUtil.get(api_url, params)
    try:
        return response.json()
    except Exception:
        print(response.text)
        return demjson.decode(str(response.text))


def aes_base64_decode_to_string(data, iv="SK8bncVu", key="OW84U8Eerdb99rtsTXWSILDO"):
    return unpad(DES3.new(key.encode(), DES3.MODE_CBC, iv.encode()).decrypt(base64.b64decode(data)),
                 DES3.block_size).decode()


class Book:

    @staticmethod
    def novel_info(novel_id: str):
        response = HttpUtil.get("https://infosxs.pysmei.com/BookFiles/Html/{}/info.html".format(novel_id)).json()
        if response is not None and response.get('info') == 'success':
            return response.get('data')

    @staticmethod
    def catalogue(novel_id):
        novel_id = str(int(int(novel_id) / 1000) + 1) + "/" + str(novel_id)
        response = HttpUtil.get("https://infosxs.pysmei.com/BookFiles/Html/{}/index.html".format(novel_id))
        if response:
            catalogue_info_list = re.findall(r'{"id":(\d+),"name":"(.*?)","hasContent":(\d+)}', response.text)
            if catalogue_info_list:
                index = 0
                for catalogue_info in catalogue_info_list:
                    index += 1
                    chapter_name = catalogue_info[1]
                    if "{{{}}}" in chapter_name:
                        chapter_name = aes_base64_decode_to_string(chapter_name[chapter_name.index("{{{}}}") + 6:])
                    yield {
                        'chapter_id': catalogue_info[0],
                        'chapter_name': chapter_name,
                        'volume_index': index
                    }

    @staticmethod
    def content(novel_id, chapter_id: str):
        response = HttpUtil.get("https://contentxs.pysmei.com/BookFiles/Html/{}/{}.html".format(
            str(int(int(novel_id) / 1000) + 1) + "/" + str(novel_id), chapter_id)).json()
        if response and response.get('info') == 'success':
            if "{{{}}}" in response["data"]["content"]:
                response["data"]["content"] = aes_base64_decode_to_string(
                    response["data"]["content"][response["data"]["content"].index("{{{}}}") + 6:])
            return response.get('data')

    @staticmethod
    def search(key: str, page: int = 1):
        params = {"key": key, "page": page, "siteid": "app2"}
        response = get("https://souxs.leeyegy.com/search.aspx", params=params)
        if response is not None and response.get('info') == 'success':
            return response.get('data')


class Cover:
    @staticmethod
    def download_cover(url: str, params: dict = None) -> bytes:
        response = HttpUtil.get(url, params=params)
        if response:
            return response.content
        print('[ERROR COVER]', url)
