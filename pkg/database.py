from peewee import SqliteDatabase, Model, CharField, IntegerField

# create sqlite
db = SqliteDatabase('biquge.db')


# 定义模型类
class Chapter(Model):
    chapter_title = CharField()
    volume_title = CharField()
    volume_index = IntegerField()
    chapter_content = CharField()
    chapter_id = IntegerField()
    book_id = IntegerField()

    class Meta:
        database = db


class Book(Model):
    book_name = CharField()
    book_author = CharField()
    book_state = CharField()
    book_updated = CharField()
    book_intro = CharField()
    book_id = IntegerField()

    class Meta:
        database = db


# 连接数据库并创建表格
db.connect()
db.create_tables([Chapter, Book])