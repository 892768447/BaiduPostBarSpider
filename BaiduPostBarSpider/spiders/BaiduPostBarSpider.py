#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017年8月29日
@author: Irony."[讽刺]
@site: alyl.vip, orzorz.vip, irony.coding.me , irony.iask.in , mzone.iask.in
@email: 892768447@qq.com
@file: spiders.BaiduPostBarSpider
@description: 
'''
import json
from random import choice

from scrapy.http import Request
from scrapy.spiders import Spider

from BaiduPostBarSpider.models import dbInit, ForumModel


__version__ = "0.0.1"

UserAgents = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) ",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36"
]

Headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Cache-Control": "max-age=0",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "",
}


class BaiduPostBarSpider(Spider):
    '''
    #百度贴吧爬虫
    '''
    name = "BaiduPostBarSpider"  # 锦江学院
    allowed_domains = ["tieba.baidu.com"]  # 允许的域名
    ForumUrl = "http://tieba.baidu.com/p/%s"  # 帖子详情

    def __init__(self, *args, **kwargs):
        super(BaiduPostBarSpider, self).__init__(*args, **kwargs)
        self.Session = dbInit()  # 初始化数据库连接池

    '''
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # 初始化数据库连接池
        setattr(crawler.settings, "Session", dbInit())
#         crawler.settings["Session"] = dbInit()
        return super(BaiduPostBarSpider, cls).from_crawler(crawler, *args, **kwargs)
    '''

    def start_requests(self):
        start_urls = [  # 需要爬取地址
            "http://tieba.baidu.com/f?kw=锦江学院&ie=utf-8&pn=pn".format(
                pn=pn * 50
            ) for pn in range(0, 1)  # 最大的页数(10页)
        ]
        for url in start_urls:
            headers = Headers.copy()  # 复制一份
            headers["User-Agent"] = choice(UserAgents)  # 随机一份user agent
            yield Request(url, callback=self.parse_forum_list, headers=headers, dont_filter=True)

    def parse_forum_list(self, response):
        # 提取所有帖子的id和作者
        session = self.Session()
        for data in response.xpath('//li[contains(@class,"j_thread_list")]/@data-field').extract():
            data = json.loads(data)  # 解析为json格式
            model = ForumModel(**{
                "post_id": data.get("id", ""),
                "author_name": data.get("author_name", ""),
                "reply_num": data.get("reply_num", "")
            })
            session.merge(model)
            headers = Headers.copy()  # 复制一份
            headers["User-Agent"] = choice(UserAgents)  # 随机一份user agent
            yield Request(self.ForumUrl % data.get("id", ""), callback=self.parse_forum, headers=headers, dont_filter=True)
        session.commit()
        session.close()
        '''
        #使用item处理
        for data in response.xpath('//li[contains(@class,"j_thread_list")]/@data-field').extract():
            data = json.loads(data)  # 解析为json格式
            item = ForumListItem(
                post_id=data.get("id", ""),
                author_name=data.get("author_name", ""),
                reply_num=data.get("reply_num", ""),
            )
            yield item
        '''
    
    def parse_forum(self, response):
        pass