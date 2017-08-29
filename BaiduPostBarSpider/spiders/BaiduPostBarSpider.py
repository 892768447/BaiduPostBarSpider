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

from scrapy.spiders import Spider

from .. items import ForumListItem  # @UnresolvedImport


__version__ = "0.0.1"


class BaiduPostBarSpider(Spider):
    '''
    #百度贴吧爬虫
    '''
    name = "BaiduPostBarSpider"  # 锦江学院
    allowed_domains = ["tieba.baidu.com"]  # 允许的域名
    start_urls = [
        "http://tieba.baidu.com/f?kw=锦江学院&ie=utf-8&pn=pn".format(
            pn=pn * 50
        ) for pn in range(0, 10)  # 最大的页数(10页)
    ]

    start_urls = ["http://tieba.baidu.com/f?kw=锦江学院&ie=utf-8"]

    def parse(self, response):
        # 提取所有帖子的id和作者
        for data in response.xpath('//li[contains(@class,"j_thread_list")]/@data-field').extract():
            data = json.loads(data)  # 解析为json格式
            item = ForumListItem(
                post_id=data.get("id", ""),
                author_name=data.get("author_name", ""),
                reply_num=data.get("reply_num", ""),
            )
            yield item
