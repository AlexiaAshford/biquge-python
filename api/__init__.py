import re
import base64
from . import util
from Crypto.Cipher import DES3
from Crypto.Util.Padding import unpad


def get_new_book_id(novel_id):
    return "https://infosxs.pysmei.com/BookFiles/Html/{}/{}/".format(int(int(novel_id) / 1000) + 1, novel_id)


AES_IV = "SK8bncVu"
AES_KEY = "OW84U8Eerdb99rtsTXWSILDO"

SUCCESS_INFO = "success"


def aes_base64_decode_to_string(data: str, iv: str = AES_IV, key: str = AES_KEY) -> str:
    return unpad(DES3.new(key.encode(), DES3.MODE_CBC, iv.encode()).decrypt(base64.b64decode(data)),
                 DES3.block_size).decode()


class Book:
    @staticmethod
    def novel_info(novel_id: str) -> dict:
        response = util.get(get_new_book_id(novel_id) + "info.html")
        if response.get('info') == SUCCESS_INFO:
            return response.get('data')

    @staticmethod
    def catalogue(novel_id: str):
        catalogue_info_text = util.get(get_new_book_id(novel_id) + "index.html")
        if isinstance(catalogue_info_text, str):
            catalogue_info_list = re.findall(r'{"id":(\d+),"name":"(.*?)","hasContent":(\d+)}', catalogue_info_text)
            for index, (chapter_id, chapter_name, has_content) in enumerate(catalogue_info_list, start=1):
                chapter_name = aes_base64_decode_to_string(chapter_name[chapter_name.index("{{{}}}") + 6:]) \
                    if "{{{}}}" in chapter_name else chapter_name
                yield {
                    'chapter_id': chapter_id,
                    'chapter_name': chapter_name,
                    'volume_index': index
                }

    @staticmethod
    def content(novel_id: str, chapter_id: str) -> dict:
        response = util.get(get_new_book_id(novel_id) + "{}.html".format(chapter_id))
        if response.get('info') == SUCCESS_INFO:
            content = response["data"]["content"]
            if "{{{}}}" in content:
                content = aes_base64_decode_to_string(content[content.index("{{{}}}") + 6:])
            response["data"]["content"] = content
            return response.get('data')

    @staticmethod
    def search(key: str, page: int = 1):
        params = {"key": key, "page": page, "siteid": "app2"}
        response = util.get("https://souxs.leeyegy.com/search.aspx", params=params)
        if response.get('info') == SUCCESS_INFO:
            return response.get('data')


class Cover:
    @staticmethod
    def download_cover(url: str, params: dict = None) -> bytes:
        try:
            response = util.get(url, params=params)
            if response:
                return response
            print('[ERROR COVER]', url)
        except Exception as e:
            print('[ERROR COVER]', url, e)
