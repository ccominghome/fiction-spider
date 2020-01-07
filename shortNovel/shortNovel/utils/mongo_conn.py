from pymongo import MongoClient
from ..settings import MONGODB_HOST, MONGODB_PORT

MONG_CONN = MongoClient(MONGODB_HOST, MONGODB_PORT, connect=False)
book_chapter = MONG_CONN['book']["book_chapter"]  # 最多的数据,书籍每个章节标题+每个章节的内容+bookid+唯一的bookid
book_column = MONG_CONN['book']["book_column"]  # 另外开启一个mongodb数据库来维护目录信息
book_detail = MONG_CONN["book"]["book_detail"]  # 用于构建索引,方便后台对数据库的快速搜索,否则数据冗余太大,可能不利于索引的命中

