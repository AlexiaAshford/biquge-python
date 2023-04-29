import os

from instance import *
import BiquPavilionAPI

from ebooklib import epub


class EpubFile:
    def __init__(self, book_info):
        self.book_info = book_info
        self.epub = epub.EpubBook()
        self.EpubList = list()
        self.path = os.path.join
        self.epub.set_language('zh-CN')
        self.epub.set_identifier(self.book_info.book_id)
        self.epub.set_title(self.book_info.book_name)
        self.epub.add_author(self.book_info.author_name)

    def add_intro(self):
        write_intro = epub.EpubHtml(title='简介信息', file_name='0000-000000-intro.xhtml', lang='zh-CN')
        content = '<html><head></head><body><h1>简介</h1>'
        content += '<p>书籍书名:{}</p><p>书籍序号:{}</p>'
        content += '<p>书籍作者:{}</p><p>更新时间:{}</p>'
        content += '<p>最新章节:{}</p><p>系统标签:{}</p>'
        content += '<p>简介信息:</p>{}</body></html>'
        write_intro.content = content.format(
            self.book_info.book_name, self.book_info.book_id,
            self.book_info.author_name, self.book_info.book_updated,
            self.book_info.last_chapter, self.book_info.book_tag, self.book_info.book_intro
        )
        self.epub.add_item(write_intro)
        self.EpubList.append(write_intro)

    def cover(self):
        if "http" not in self.book_info.cover_url:
            if self.book_info.cover_url[-1] == "/":
                self.book_info.cover_url = self.book_info.cover_url[:-1]
            self.book_info.cover_url = "https://imgapixs.pysmei.com/BookFiles/BookImages/" + self.book_info.cover_url

        # print(self.book_info.cover_url)
        cover_jpg = BiquPavilionAPI.Cover.download_cover(self.book_info.cover_url)
        self.epub.set_cover(self.book_info.book_name + '.png', cover_jpg)

    def add_chapter(self, chapter_id: str, chapter_title: str, content: str, serial_number: str):
        file_name = str(int(serial_number) + 1).rjust(4, "0") + '-' + str(chapter_id) + '.xhtml'
        chapter_serial = epub.EpubHtml(
            title=chapter_title, file_name=file_name, lang='zh-CN', uid='index-{}'.format(int(serial_number) + 1)
        )
        chapter_serial.content = content.replace('\n', '</p>\r\n<p>')
        self.epub.add_item(chapter_serial)
        self.EpubList.append(chapter_serial)

    def save(self):
        self.cover()
        self.epub.toc = tuple(self.EpubList)
        self.epub.spine = ['nav']
        self.epub.spine.extend(self.EpubList)
        self.epub.add_item(epub.EpubNcx())
        self.epub.add_item(epub.EpubNav())
        save_book_dir = os.path.join(Vars.cfg.data.get('save_book'), self.book_info.book_name,
                                     f'{self.book_info.book_name}.epub')
        epub.write_epub(save_book_dir, self.epub, {})
