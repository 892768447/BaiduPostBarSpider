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

from scrapy.http import Request
from scrapy.spiders import Spider

from BaiduPostBarSpider.items import ForumListItem, ForumTitleItem
from BaiduPostBarSpider.models import dbInit  # @UnresolvedImport


__version__ = "0.0.1"

# 好像会影响xpath解析,坑
# UserAgents = [
#     "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
# ]

Headers = {
    "Accept": "text/html, application/xhtml+xml, image/jxr, */*",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
}


class BaiduPostBarSpider(Spider):
    '''
    #百度贴吧爬虫
    '''
    name = "BaiduPostBarSpider"  # 锦江学院
    allowed_domains = ["tieba.baidu.com"]  # 允许的域名
    Schools = ["锦江学院"]
    MaxPage = 1  # 最大10页
    ForumListUrl = "http://tieba.baidu.com/f?kw={kw}&ie=utf-8&pn={pn}"
    ForumUrl = "http://tieba.baidu.com{uri}"  # 帖子详情

    # 提取页面帖子信息
    ForumListXpath = '//li[normalize-space(@class)="j_thread_list clearfix"]/@data-field'
    # 提取页面帖子链接
    ForumUrlXpath = '//li[normalize-space(@class)="j_thread_list clearfix"]//a[normalize-space(@class)="j_th_tit"]/@href'
    # 提取帖子标题
    ForumTitleXpath = '//h1[contains(@class,"core_title_txt")]/text()'

    def __init__(self, *args, **kwargs):
        super(BaiduPostBarSpider, self).__init__(*args, **kwargs)
#         self.Session = dbInit()  # 初始化数据库连接池
        self.start_urls = [  # 需要爬取地址
            self.ForumListUrl.format(
                kw=kw, pn=pn * 50
            ) for kw in self.Schools for pn in range(0, self.MaxPage)
        ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # 初始化数据库连接池
        setattr(crawler.settings, "Session", dbInit())
#         crawler.settings["Session"] = dbInit()
        return super(BaiduPostBarSpider, cls).from_crawler(crawler, *args, **kwargs)

    '''
    def getUserAgent(self):
        # 随机
        headers = Headers.copy()  # 复制一份
        headers["User-Agent"] = choice(UserAgents)  # 随机一份user agent
        return headers
    '''

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_forum_list,
                          headers=Headers)

    def parse_forum_list(self, response):
        # 提取所有帖子的id和作者
        self.log("parse_forum_list")
        # 交给Forum Item Pipline处理
        item = ForumListItem(
            data_field=response.xpath(self.ForumListXpath).extract()
        )
        self.log("yield item")
        yield item
        self.log("start into forum url")
        for uri in response.xpath(self.ForumUrlXpath).extract():
            # 进入该帖子爬取内容和页数
            yield Request(self.ForumUrl.format(uri=uri),
                          meta={"post_id": uri.split("/")[2]},
                          callback=self.parse_forum,
                          headers=Headers)

    def parse_forum(self, response):
        self.log("parse_forum")
        item = ForumTitleItem(
            post_id=response.meta.get("post_id"),
            post_title=response.xpath(self.ForumTitleXpath).extract_first()
        )
        yield item
