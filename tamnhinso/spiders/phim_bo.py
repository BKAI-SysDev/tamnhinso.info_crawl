# -*- coding: utf-8 -*-
import scrapy


class TnsSpider(scrapy.Spider):
    name = 'phim_bo'
    allowed_domains = ['tamnhinso.info']
    start_urls = ['http://tamnhinso.info/phim/phim-bo/viewbycategory']

    def parse(self, response):
        pass
