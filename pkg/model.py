from pydantic import BaseModel, Field
from typing import List, Optional


class Book(BaseModel):
    cover_url: Optional[str] = Field(..., title="封面链接", alias="Img", description="封面链接")
    book_name: Optional[str] = Field(..., title="书名", alias="Name", description="书名")
    book_tag: Optional[str] = Field(..., title="标签", alias="CName", description="标签")
    book_intro: Optional[str] = Field(..., title="简介", alias="Desc", description="简介")
    author_name: Optional[str] = Field(..., title="作者", alias="Author", description="作者")
    book_updated: Optional[str] = Field(None, title="更新时间", alias="LastTime", description="更新时间")
    book_state: Optional[str] = Field(..., title="状态", alias="BookStatus", description="状态")
    book_id: Optional[str] = Field(..., title="书籍ID", alias="Id", description="书籍ID")
    last_chapter: Optional[str] = Field(..., title="最新章节", alias="LastChapter", description="最新章节")
    CId: Optional[int] = None
    FirstChapterId: Optional[int] = None
    LastChapterId: Optional[int] = None
    SameUserBooks: Optional[list] = None
    SameCategoryBooks: Optional[list] = None
    BookVote: Optional[dict] = None
    UpUser: Optional[str] = None
    Declare: Optional[str] = None
    CloudList: Optional[list] = None
