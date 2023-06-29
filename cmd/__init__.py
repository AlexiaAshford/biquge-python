import api
import book
import epub
from pkg import database
from instance import *
from prettytable import PrettyTable


class Command:
    @staticmethod
    def download(book_id: str, close_epub: bool):  # 通过小说ID下载单本小说
        response = api.Book.novel_info(book_id)
        if isinstance(response, dict):
            book_info = book.BookDownload(response)
            if "{{{}}}" in book_info.book_info.book_name:
                book_info.book_info.book_name = api.aes_base64_decode_to_string(
                    book_info.book_info.book_name[book_info.book_info.book_name.index("{{{}}}") + 6:])

                book_info.book_info.author_name = api.aes_base64_decode_to_string(
                    book_info.book_info.author_name[book_info.book_info.author_name.index("{{{}}}") + 6:])

            if not database.Book.select().where(database.Book.book_id == book_id).exists():
                database.Book.create(book_id=book_id, book_name=book_info.book_info.book_name,
                                     book_author=book_info.book_info.author_name,
                                     book_state=book_info.book_info.book_state,
                                     book_updated=book_info.book_info.book_updated,
                                     book_intro=book_info.book_info.book_intro)

            makedirs(Vars.cfg.data.get('save_book') + "/" + book_info.book_info.book_name)
            book_info.show_book_info()
            book_info.download_chapter_threading()
        else:
            return print("获取书籍信息失败，请检查id或者重新尝试！")

        epub_add_chapters = []

        # 通过chapter_index排序
        chapter_list = database.Chapter.select().group_by(database.Chapter.chapter_index).where(
            database.Chapter.book_id == book_id)
        for res in chapter_list:  # 获取目录文,并且 遍历文件名
            epub_add_chapters.append((res.chapter_id, res.chapter_title, res.chapter_content, res.chapter_index))
            write(book_info.save_book_dir, 'a', res.chapter_title + '\n' + res.chapter_content + '\n\n')

        if close_epub:
            epub_info = epub.EpubFile(book_info.book_info).add_intro()
            for chapter in epub_add_chapters:
                epub_info.add_chapter(*chapter)
            epub_info.save()

        print("《{}》下载完成".format(book_info.book_info.book_name))

        database.db.close()

    @staticmethod
    def search(key: str, page: int, open_epub: bool):
        response = api.Book.search(key, page)
        table = PrettyTable(["编号", "书名", "作者", "状态", "更新时间", "最新章节"])
        for index, books in enumerate(response):
            table.add_row([index, books.get('Name'), books.get('Author'), books.get('BookStatus'),
                           books.get('UpdateTime'), books.get('LastChapter')])

        print(table)
        print("please input the book id index to download:")
        while True:
            book_id_index = input_str('>').strip()
            if book_id_index.isdigit() and int(book_id_index) < len(response):
                Command.download(response[int(book_id_index)]["Id"], open_epub)
                break
            else:
                print("please input the book id index to download, the index must be a number.")

    @staticmethod
    def update(limit: int, filename: str, open_epub: bool):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                book_list = []
                for line in f:
                    match = re.match(r'^\s*([0-9]{1,7}).*$', line)
                    if match is not None:
                        book_list.append(match.group(1))
                        if len(book_list) >= limit > 0:
                            break

                start = time.time()
                for book_id in book_list:
                    Command.download(book_id, open_epub)

                print(f'下载耗时:{round(time.time() - start, 2)} 秒')
        except FileNotFoundError:
            print(f"{filename} 文件不存在")
