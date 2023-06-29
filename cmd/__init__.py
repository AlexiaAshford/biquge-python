import os
import api
import sys
import book
import epub
from pkg import database
from instance import *
from prettytable import PrettyTable


def agreed_read_readme():
    if Vars.cfg.data.get('Disclaimers') != 'yes':
        print(Msg.msg_agree_terms)
        confirm = input_str('>').strip()
        if confirm == 'yes' or confirm == '同意':
            Vars.cfg.data['Disclaimers'] = 'yes'
            Vars.cfg.save()
        else:
            sys.exit()


def download_book(book_id: str, close_epub: bool):  # 通过小说ID下载单本小说
    response = api.Book.novel_info(book_id)
    if isinstance(response, dict):
        book_info = book.BookDownload(response)
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
        epub_info = epub.EpubFile(book_info.book_info)
        epub_info.add_intro()
        epub_add_chapters_length = len(epub_add_chapters)
        for index, chapter in enumerate(epub_add_chapters, start=1):
            epub_info.add_chapter(*chapter)
            print("epub output progress: {}/{}".format(index, epub_add_chapters_length), end='\r')
        epub_info.save()

    print("《{}》下载完成".format(book_info.book_info.book_name))

    database.db.close()


def search_book(key: str, page: int, open_epub: bool):
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
            download_book(response[int(book_id_index)]["Id"], open_epub)
            break
        else:
            print("please input the book id index to download, the index must be a number.")


def update_book_list(limit: int, filename: str, open_epub: bool):
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
                download_book(book_id, open_epub)

            print(f'下载耗时:{round(time.time() - start, 2)} 秒')
    except FileNotFoundError:
        print(f"{filename} 文件不存在")
