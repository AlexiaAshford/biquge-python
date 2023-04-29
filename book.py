import os

import BiquPavilionAPI
from instance import *
from pkg import model
from tqdm import tqdm
from pkg import database
from concurrent.futures import ThreadPoolExecutor, as_completed

from prettytable import PrettyTable


class BookDownload:

    def __init__(self, book_info: dict):
        try:
            self.book_info = model.Book(**book_info)
        except Exception as e:
            quit(str(e))

        self.save_book_dir = None
        self.chapter_list = []
        self.add_database_pool = []

    def show_book_info(self):
        # Define the table structure
        table = PrettyTable(["信息类型", "信息"])
        table.add_row(["作者", self.book_info.author_name])
        table.add_row(["状态", self.book_info.book_state])
        table.add_row(["最新章节", self.book_info.last_chapter])
        table.add_row(["更新", self.book_info.book_updated])
        if len(self.book_info.book_intro) >= 20:
            table.add_row(["简介", self.book_info.book_intro[:20] + '...'])
        else:
            table.add_row(["简介", self.book_info.book_intro])

        self.save_book_dir = os.path.join(Vars.cfg.data.get('save_book'), self.book_info.book_name,
                                          f'{self.book_info.book_name}.txt')
        write(self.save_book_dir, 'w', "书名：" + self.book_info.book_name + "\n")
        write(self.save_book_dir, 'a', "作者：" + self.book_info.author_name + "\n")
        write(self.save_book_dir, 'a', "状态：" + self.book_info.book_state + "\n")
        write(self.save_book_dir, 'a', "最新章节：" + self.book_info.last_chapter + "\n")
        write(self.save_book_dir, 'a', "更新：" + self.book_info.book_updated + "\n")
        write(self.save_book_dir, 'a', "简介：" + self.book_info.book_intro + "\n")

        print(table)

    def arrange(self, intro: str, new_intro: str = "", width: int = 60) -> str:
        for line in intro.splitlines():
            intro_line = line.strip().strip("　")
            if intro_line != "":
                new_intro += "\n" + intro_line[:width]
        return new_intro

    def download_content_threading(self, chapter_info) -> None:
        content_info = BiquPavilionAPI.Chapter.content(self.book_info.book_id, chapter_info.get('id'))
        if chapter_info.get('name') != "该章节未审核通过" and \
                "正在更新中，请稍等片刻，内容更新后" not in content_info.get('content'):
            self.add_database_pool.append(database.Chapter(
                chapter_title=chapter_info.get('name'),
                chapter_content=content_info.get('content'),
                chapter_id=chapter_info.get('id'),
                volume_title=chapter_info.get('volume_name'),
                volume_index=chapter_info.get('volume_index'),
                book_id=self.book_info.book_id
            ))

    def download_chapter_threading(self):
        download_chapter_list = []
        response = BiquPavilionAPI.Book.catalogue(self.book_info.book_id)
        for index, catalogue_info in enumerate(response, start=1):
            print(f"第{index}卷", catalogue_info.get('name'))
            for info in catalogue_info.get('list'):
                info['volume_name'] = catalogue_info.get('name')
                info['volume_index'] = index
                self.chapter_list.append(info)
                if not database.Chapter.select().where(database.Chapter.chapter_id == info.get('id')).first():
                    download_chapter_list.append(info)

        if len(download_chapter_list) == 0:
            return print("没有需要下载的章节！")
        with ThreadPoolExecutor(max_workers=Vars.cfg.data.get('threading_pool_size')) as executor:
            threading_pool = []
            for chapter_info in download_chapter_list:
                threading_pool.append(
                    executor.submit(self.download_content_threading, chapter_info)
                )
            tqdm_threading_pool = tqdm(as_completed(threading_pool), total=len(download_chapter_list),
                                       desc="下载进度", ncols=80)
            for thread in as_completed(threading_pool):
                tqdm_threading_pool.update(1)
                thread.result()
            tqdm_threading_pool.close()
        with database.db.atomic():
            database.Chapter.bulk_create(self.add_database_pool, batch_size=200)
