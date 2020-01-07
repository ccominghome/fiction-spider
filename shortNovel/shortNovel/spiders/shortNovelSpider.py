# coding=utf-8

import scrapy
from scrapy.http import Request
from ..utils.mongo_conn import book_detail, book_column, book_chapter
from ..utils.utils import generate_unique_fingerprint_for_unique_chapter_id


class shortNovelSpider(scrapy.Spider):
    page = 2
    name = 'shortNovel'
    allowed_domains = ['shubaowang123.cc']

    def start_requests(self):
        urls = ['http://www.shubaowang123.cc/16_16566/']
        for i in range(len(urls)):
            yield Request(urls[i], self.parse_novel)

    def parse_novel(self, response):

        chaptersLink = response.xpath('//*[@id="wrapper"]/div[6]/div/dl/dd/a/@href').extract()
        chaptersTitle = response.xpath('//*[@id="wrapper"]/div[6]/div/dl/dd/a/text()').extract()
        book_name = response.xpath('//*[@id="info"]/h1/text()').extract()
        book_auth = response.xpath('//*[@id="info"]/p[1]/text()').extract()
        book_img = response.xpath('//*[@id="fmimg"]/img').extract()
        book_img = book_img[0].split('"')
        book_img = book_img[1]
        book_source_id = generate_unique_fingerprint_for_unique_chapter_id(book_name[0], book_auth[0])
        book_category = "其他分类"
        book_score = "8"
        book_source = "Jiaston"
        book_gender = "男生"
        book_id = book_source_id + book_source
        book_last_time = response.xpath('//*[@id="info"]/p[3]/text()').extract()
        book_last_time = book_last_time[0].split('：', 1)
        book_last_chapter_name = chaptersTitle[-1]
        book_status = "完结"

        bookdetail = {"book_source_id": book_source_id,
                      "book_name": book_name[0],
                      "book_author": book_auth[0],
                      "book_img": book_img,
                      "book_desc": "",
                      "book_category": book_category,
                      "book_score": book_score,
                      "book_gender": book_gender,
                      "book_source": book_source,
                      "book_id": book_id,
                      "book_last_time": book_last_time[1],
                      "book_last_chapter_name": book_last_chapter_name,
                      "book_status": book_status
                      }
        if book_detail.find_one({"book_source_id": bookdetail["book_source_id"]}):
            book_detail.update_many({"book_source_id": bookdetail["book_source_id"]},
                                    {"$set": {"book_last_time": bookdetail["book_last_time"],
                                              "book_last_chapter_name": bookdetail["book_last_chapter_name"],
                                              "book_status": bookdetail["book_status"]}})

        else:
            book_detail.insert_one(bookdetail)

        column_list = []
        for chapter_id, chapter_name in zip(chaptersLink, chaptersTitle):
            bookcolumn = {
                "hasContent": 1,
                "chapter_source_id": chapter_id,
                "chapter_name": chapter_name,
                "chapter_id": generate_unique_fingerprint_for_unique_chapter_id(
                    bookdetail.get("book_source_id"), chapter_id)
            }
            column_list.append(bookcolumn)

        if book_column.find_one({"book_source_id": bookdetail["book_source_id"]}):
            x = book_column.update_one({"book_source_id": bookdetail["book_source_id"]},
                                       {"$set": {"column": column_list}})

        else:
            book_column.insert_one({"book_source_id": bookdetail["book_source_id"],
                                    "book_id": bookdetail["book_id"],
                                    "column": column_list})

        # 获取每一章节
        for link in reversed(chaptersLink):
            book_item = {"book_source_id": bookdetail["book_source_id"],
                         "book_id": bookdetail["book_id"],
                         "chapter_source_id": link,
                         "chapter_id": generate_unique_fingerprint_for_unique_chapter_id(
                             bookdetail.get("book_source_id"), link)}
            link = 'https://www.shubaowang123.cc' + link
            yield Request(link, meta={'item': book_item}, callback=self.parse_chapter)

    def parse_chapter(self, response):
        chapterName = response.xpath('//*[@class="bookname"]/h1/text()').extract()
        chapterText = response.xpath('//*[@id="content"]/text()').extract()

        book_item = response.meta['item']
        book_content = ''
        for i in range(len(chapterText)):
            book_content = book_content + chapterText[i]

        book_chapter.insert_one({"book_source_id": book_item['book_source_id'],
                                 "book_id": book_item['book_id'],
                                 "chapter_source_id": book_item['chapter_source_id'],
                                 "chapter_name": ''.join(chapterName),
                                 "chapter_id": book_item['chapter_id'],
                                 "chapter_content": book_content
                                 })
