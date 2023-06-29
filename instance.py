import re
import time
from config import *


class Vars:
    cfg = Config('Config.json', os.getcwd())
    book_info = None
    epub_info = None


def mkdir(file_path: str):
    if not os.path.exists(file_path):
        os.mkdir(file_path)


def makedirs(file_path: str):
    if not os.path.exists(os.path.join(file_path)):
        os.makedirs(os.path.join(file_path))


def input_str(prompt, default=None):
    while True:
        ret = input(prompt)
        if ret != '':
            return ret
        elif default is not None:
            return default


def del_title(title: str):
    """删去windowns不规范字符"""
    return re.sub(r'[？?。*|“<>:/\\]', '', title.replace("\x06", "").replace("\x05", "").replace("\x07", ""))


def write(path: str, mode: str, info=None):
    if info is not None:
        try:
            with open(path, f'{mode}', encoding='UTF-8', newline='') as file:
                file.writelines(info)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            with open(path, f'{mode}', encoding='gbk', newline='') as file:
                file.writelines(info)
    else:
        try:
            return open(path, f'{mode}', encoding='UTF-8')
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            return open(path, f'{mode}', encoding='gbk')


def setup_config():
    Vars.cfg.load()
    config_change = False
    if type(Vars.cfg.data.get('save_book')) is not str or Vars.cfg.data.get('save_book') == "":
        Vars.cfg.data['save_book'] = 'novel'
        config_change = True
    if type(Vars.cfg.data.get('threading_pool_size')) is not int or Vars.cfg.data.get('threading_pool_size') == "":
        Vars.cfg.data['threading_pool_size'] = 12
        config_change = True
    if type(Vars.cfg.data.get('Disclaimers')) is not str or Vars.cfg.data.get('Disclaimers') == "":
        Vars.cfg.data['Disclaimers'] = 'No'
        config_change = True

    if config_change:
        Vars.cfg.save()
        if not os.path.exists(Vars.cfg.data.get('save_book')):
            mkdir(Vars.cfg.data.get('save_book'))


class Msg:
    msg_help = [
        '输入指令\nd | bookid\t\t\t\t\t———输入书籍序号下载单本小说',
        's | search-book\t\t\t\t\t———下载单本小说',
        'h | help\t\t\t\t\t———获取使用程序帮助',
        'q | quit\t\t\t\t\t———退出运行的程序',
        'p | thread-max\t\t\t\t\t———改变线程数目',
        'u | update\t\t\t\t\t———下载指定文本中的book-id '
    ]
    msg_agree_terms = """ 
是否已经仔细阅读并同意本项目的免责声明和LICENSE中的条款？ 
免责声明：本项目仅用于开源学习，不得将其用于任何商业盈利行为。使用者应自行承担因使用本项目而产生的一切风险和责任。  
本项目采用MIT License。在遵守本协议的前提下，您可以自由地使用、复制、修改和分发本项目。更多信息请参考LICENSE文件。
"如果同意声明，请输入英文 \"yes\" 或者中文 \"同意\" 后按Enter建，如果不同意请关闭此程式"""

    msg_user_agent = [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
        "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
    ]
