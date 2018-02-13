# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader

from ArticleSpider.utils.common import get_md5

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["blog.jobbole.com"]
    start_urls = ['http://blog.jobbole.com/all-posts/']
    #start_urls = ['http://blog.jobbole.com/111096/']
    def parse(self, response):
        '''
        两件事：
        1.把列表页的每篇文章url提取出来，然后调用下面的parse_detail解析每一篇文章详细
        2.或许列表页的下一页，然后使用parse循环这个步骤
        '''

    #   post_nodes = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            #   这里的Request,callback是使用了twitted异步
            post_url = post_node.css("::attr(href)").extract_first("")  # 默认为空
            image_url = post_node.css("img::attr(src)").extract_first("")
            #   只获取到a标签seletor,在进一步获取seleltor,获取列表页的图片url和文章url
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail)

        #   获取下一页
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)


    def parse_detail(self, response):

        # 通过itemloader 加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)

        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()

        yield article_item  # 这样item的数据就会传到pipelines,做进一步数据处理，如存储，去重，xxx

