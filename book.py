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
        for i in range(3):
            content_info = BiquPavilionAPI.Book.content(self.book_info.book_id, chapter_info.get('chapter_id'))
            if content_info:
                res = database.Chapter(
                    chapter_title=chapter_info.get('chapter_name'),
                    chapter_content=content_info.get('content'),
                    chapter_id=chapter_info.get('chapter_id'),
                    chapter_index=chapter_info.get('volume_index'),
                    book_id=self.book_info.book_id
                )
                res.save()
                break
            else:
                print(chapter_info, "下载失败，正在重试！")

    def download_chapter_threading(self):
        download_chapter_list = []
        response = BiquPavilionAPI.Book.catalogue(self.book_info.book_id)
        if not response:
            print("获取章节列表失败！")
            return
        for index, catalogue in enumerate(response, start=1):
            if not database.Chapter.select().where(database.Chapter.chapter_id == catalogue.get('chapter_id')).first():
                download_chapter_list.append(catalogue)

        if len(download_chapter_list) == 0:
            return print("没有需要下载的章节！")
        with ThreadPoolExecutor(max_workers=64) as executor:
            threading_pool = []
            for chapter_info in download_chapter_list:
                threading_pool.append(
                    executor.submit(self.download_content_threading, chapter_info)
                )
            tqdm_threading_pool = tqdm(as_completed(threading_pool), total=len(download_chapter_list),
                                       desc="下载进度", ncols=80)
            for thread in as_completed(threading_pool):
                thread.result()
                tqdm_threading_pool.update(1)

            tqdm_threading_pool.close()
        # with database.db.atomic():
        #     database.Chapter.bulk_create(self.add_database_pool, batch_size=200)
