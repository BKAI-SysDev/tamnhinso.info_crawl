# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.shell import inspect_response
from scrapy.linkextractors import LinkExtractor
from w3lib.html import remove_tags
from scrapy_splash import SplashRequest
import re


class TnsSpider(scrapy.Spider):
    name = 'phim_bo'
    allowed_domains = ['tamnhinso.info']
    start_urls = [
       'http://tamnhinso.info/phim/phim-bo/viewbycategory'
    ]
    script = """
                function main(splash)
                    splash.html5_media_enabled = true
                    splash.private_mode_enabled = false
                    local url = splash.args.url
                    assert(splash:go(url))
                    assert(splash:wait(4))
                    return splash:html()
                end
            """

    link_films = dict()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url = url,callback=self.parse_list_film)
    
    def parse_list_film(self,response):
        for url in list(map(lambda x: x.url, (LinkExtractor(restrict_xpaths="//div[@class = 'col-md-2 col-xs-6 movie-item']").extract_links(response)))):
            yield Request(url=url, callback=self.parse_film_info)
    
    def parse_film_info(self,response):
        key = list(map(remove_tags,response.xpath("//div[@class = 'cf pt-30 row']/div[@class = 'col-md-6 ']/table/tr/td[1]").getall()))
        vals = list(map(remove_tags,response.xpath("//div[@class = 'cf pt-30 row']/div[@class = 'col-md-6 ']/table/tr/td[2]").getall()))
        i = list(map(remove_tags,response.xpath("//div[@class = 'col-md-12']/div[@class = 'movie-desc']").getall()))
        btn = list(map(remove_tags,response.xpath("//div[@class = 'mt-10']").getall()))
        intro = i[0].strip()
        val = []
        for v in vals:
            val.append(v.strip())
        result = dict(zip(key,val))
        result["intro"] = intro
        btn = btn[0].strip()
        if(btn == 'XEM PHIM'):
            # episode_btn = list(map(remove_tags,response.xpath("//div[@class = 'col-md-6']/ul[@class = 'chap-list']/li/a").getall()))
            # episode_btn = list(map(lambda x:x.strip(),episode_btn))   
            # link_films = dict()
            video_btn = LinkExtractor(restrict_xpaths="//div[@class = 'col-md-6']/ul[@class = 'chap-list']/li").extract_links(response)
            for x in video_btn:
                link = x.url
                yield SplashRequest(url= link,callback = self.parse_link_film,endpoint = 'execute',args={'lua_source': self.script,'wait':8,'timeout':3600},meta = {"url":link})
            result['links'] = self.link_films
            self.link_films.clear()
            inspect_response(self,response)
            yield result
        else:
           yield None

    def parse_link_film(self,response):
        url = response.meta.get("url")
        pattern=re.compile(r'(?<=tap-)(\d+)')
        episode = pattern.findall(url)
        self.link_films[episode[0]] = self.get_link(response)


    def get_link(self,response):
        link = dict()
        link_720 = response.xpath("//source[@label = '720']/@src").getall()
        link_360 = response.xpath("//source[@label = '360']/@src").getall()
        link["360p"] = link_360
        link["720p"] = link_720
        return link
    

    # docker run command:docker run -p 8050:8050 scrapinghub/splash --max-timeout 3600