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
import math
from time import time

from scrapy.http import Request
from scrapy.spiders import Spider

from BaiduPostBarSpider.items import ForumListItems, ForumInfosItem, \
    LzlCommentItem
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
    LzlPageSize = 10  # 楼中楼一页的显示数量
    ForumListUrl = "http://tieba.baidu.com/f?kw={kw}&ie=utf-8&pn={pn}"
    ForumUrl = "http://tieba.baidu.com/p/{tid}"  # 帖子详情
    ForumNexUrl = "http://tieba.baidu.com/p/{tid}?pn={pn}"  # 帖子下一页
    # 楼中楼回复,tid帖子id,pid为主回复id,pn为楼中楼回复分页,t随机时间
    LzlUrl = "https://tieba.baidu.com/p/comment?tid={tid}&pid={pid}&pn={pn}&t={t}"

    # 提取页面帖子信息
    ForumListXpath = '//li[normalize-space(@class)="j_thread_list clearfix"]'
    # 提取页面帖子ID
    ForumListIdsRegx = '"id":(\d+),'
    # 提取页面帖子作者
    ForumListAuthorsRegx = '"author_name":"(.*?)",'
    # 提取页面帖子回复数
    ForumListReplysRegx = '"reply_num":(\d+),'
    # 提取页面帖子标题
    ForumListTitlesXpath = '//li[normalize-space(@class)="j_thread_list clearfix"]//a[normalize-space(@class)="j_th_tit"]/text()'

    # 提取当页帖子的
    ForumItemsXpath = '//div[contains(@class,"l_post j_l_post l_post_bright")]'
    # 提取当前帖子页数
    ForumItemPageXpath = '//div[normalize-space(@class)="pb_footer"]//li[normalize-space(@class)="l_reply_num"][1]/span[2]/text()'
    #提取当前帖子评论ID
    ForumItemIdsRegx = '"post_id":(\d+),'
    #提取当前帖子评论人
    ForumItemAuthorsRegx = '"user_name":"(.*?)",'
    # 提取当页帖子的评论(不含楼中楼)
    ForumContentsXpath = '//cc/div/text()'
    #提取当页帖子楼中楼回复数量
    ForumItemLzlNumsRegx = '"comment_num":(\d+),'
    
    #楼中楼
    ForumItemLzlsXpath = '//li[contains(@class,"lzl_single_post j_lzl_s_p")]/@data-field'
    # 提取楼中楼回复
    ForumItemLzlContentsXpath = '//span[normalize-space(@class)="lzl_content_main"]/text()'
    # 楼中楼评论时间
    ForumItemLzlTimesXpath = '//span[normalize-space(@class)="lzl_time"]/text()'
    # 楼中楼评论用户昵称是pid
    ForumItemLzlAuthorsRegx = '"user_name":"(.*?)",'

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
        forum_data_list = response.xpath(self.ForumListXpath)
        post_ids = forum_data_list.re(self.ForumListIdsRegx).extract()
        item = ForumListItems(
            post_ids=post_ids,
            author_names=forum_data_list.re(
                self.ForumListAuthorsRegx).extract(),
            reply_nums=forum_data_list.re(self.ForumListReplysRegx).extract(),
            post_titles=response.xpath(self.ForumListTitleXpath).extract()
        )
        self.log("yield item")
        # 交给Forum Item Pipline处理
        yield item
        self.log("start into forum url")
        for tid in post_ids:
            # 进入该帖子爬取内容和页数
            yield Request(self.ForumUrl.format(tid=tid),
                          # 这里next_page是控制对第一页数据解析后提取页数然后爬取次页
                          meta={"post_id": tid, "next_page": 1},
                          callback=self.parse_forum,
                          headers=Headers)

    def parse_forum(self, response):
        self.log("parse_forum")
        # 当前帖子信息
        # #标题、页数、当页评论、当页评论人信息
        post_id = response.meta.get("post_id"),  # 当前页面帖子的ID
        post_title = response.meta.get("post_title", response.xpath(
            self.ForumTitleXpath).extract_first()),  # 标题
        page_num = response.xpath(self.ForumPageXpath).extract_first()
        forum_infos = response.xpath(self.ForumContentItemXpath)
        data_field = forum_infos.xpath(self.DataFieldXpath).extract()
        item = ForumInfosItem(
            post_id=post_id,
            post_title=post_title,
            page_num=page_num,  # 页数
            post_content=forum_infos.xpath(
                self.ForumContentsXpath).extract(),  # 评论
            data_field=data_field  # 当前页面帖子的data字段
        )
        # 由forum infos pipines处理入库
        yield item
        # 爬取楼中楼下一页
        try:
            # 从data_field中获取楼中楼总评论条数
            _content = json.loads(data_field).get("content", None)
            if _content:
                post_pid = _content.get("post_id")  # 这个post_id是主评论的ID
                lzl_comment_num = _content.get("comment_num", 0)
                # 总页数
                lzl_page_num = math.ceil(lzl_comment_num / self.LzlPageSize)
                for pn in range(1, lzl_page_num):
                    yield Request(
                        self.LzlUrl.format(
                            tid=post_id, pid=post_pid, pn=pn, t=time()),
                        meta={"post_id": post_id, "post_pid": post_pid,
                              "post_title": post_title},
                        callback=self.parse_lzl_comment,
                        headers=Headers)
        except:
            pass
        if response.meta.get("next_page", 0):  # 判断是不是循环爬取下一页
            # 继续爬取帖子下一页
            try:
                for pn in range(1, page_num):
                    yield Request(
                        self.ForumNexUrl.format(tid=post_id, pn=pn),
                        meta={"post_id": post_id, "post_title": post_title},
                        callback=self.parse_forum,  # 调用本函数继续解析,但是不循环去抓取下一页了
                        headers=Headers)
            except:
                pass

    def parse_lzl_comment(self, response):
        self.log("parse_lzl_comment")
        # 回复中的楼中楼评论解析
        item = LzlCommentItem(
            post_id=response.meta.get("post_id"),
            post_content=response.xpath(self.ForumContentsLzl).extract(),
            post_time=response.xpath(self.ForumContentsTime).extract(),
            data_field=response.xpath(self.ForumContentsData).extract(),
        )
        yield item
