import api
import concurrent.futures
from instance import *
from pkg import model
from tqdm import tqdm
from pkg import database

from prettytable import PrettyTable


class BookDownload:

    def __init__(self, book_info: dict):
        try:
            self.book_info = model.Book(**book_info)
        except Exception as e:
            quit(str(e))

        self.save_book_dir = None
        self.chapter_list = []
        self.download_failed = []

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
        content_info = api.Book.content(self.book_info.book_id, chapter_info.get('chapter_id'))
        if content_info:
            try:
                database.Chapter(
                    chapter_title=chapter_info.get('chapter_name'),
                    chapter_content=content_info.get('content'),
                    chapter_id=chapter_info.get('chapter_id'),
                    chapter_index=chapter_info.get('volume_index'),
                    book_id=self.book_info.book_id
                ).save()
            except Exception as e:
                print(e)
                print("保存章节失败！")
                self.download_failed.append(chapter_info)

        else:
            self.download_failed.append(chapter_info)

    def download_chapter_threading(self):
        response = api.Book.catalogue(self.book_info.book_id)
        if not response:
            print("获取章节列表失败！")
            return

        download_chapter_list = [catalogue for catalogue in response if not database.Chapter.select().where(
            database.Chapter.chapter_id == catalogue.get('chapter_id')).first()]

        if len(download_chapter_list) == 0:
            print("没有需要下载的章节！")
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
            futures = [executor.submit(self.download_content_threading, chapter_info) for chapter_info in
                       download_chapter_list]
            with tqdm(total=len(download_chapter_list), desc="下载进度", ncols=80) as pbar:
                for future in concurrent.futures.as_completed(futures):
                    future.result()
                    pbar.update(1)

        print("一共 {} 章节，下载失败 {} 章节".format(len(download_chapter_list), len(self.download_failed)))
        table = PrettyTable(["章节序号", "章节名", "章节ID"])
        for i in self.download_failed:
            table.add_row([i.get('volume_index'), i.get('chapter_name'), i.get('chapter_id')])
        print(table)
        self.download_failed.clear()
