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
from datetime import datetime
import logging
import math
import os
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
    Schools = [
        "锦江学院", "四川大学锦江", "成都东星航空学院", "东星航空",
        "东星航空学院", "四川工商职业技术学院", "眉山职业技术学院",
        "眉职院", "眉山城市职业技术学院", "成艺", "四川科技职业学院", "成都信息工程学院"
    ]
    MaxPage = 5  # 最大8页
    LzlPageSize = 10  # 楼中楼一页的显示数量
    ForumListUrl = "http://tieba.baidu.com/f?kw={kw}&ie=utf-8&pn={pn}"
    ForumUrl = "http://tieba.baidu.com/p/{tid}"  # 帖子详情
    ForumNexUrl = "http://tieba.baidu.com/p/{tid}?pn={pn}"  # 帖子下一页
    # 楼中楼回复,tid帖子id,pid为主回复id,pn为楼中楼回复分页,t随机时间
    LzlUrl = "https://tieba.baidu.com/p/comment?tid={tid}&pid={pid}&pn={pn}&t={t}"

    # 提取页面帖子信息
    ForumListXpath = '//li[normalize-space(@class)="j_thread_list clearfix"]/@data-field'
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
    # 提取当前帖子评论ID
    ForumItemIdsRegx = '"post_id":(\d+),'
    # 提取当前帖子评论人
    ForumItemAuthorsRegx = '"user_name":"(.*?)",'
    # 提取当前帖子主评论时间
    ForumItemDateRegx = '"date":"(\d+-\d+-\d+ \d+:\d+)",'
    # 提取当页帖子的评论(不含楼中楼)
    ForumContentsXpath = '//cc/div/text()'
    # 提取当页帖子楼中楼回复数量
    ForumItemLzlNumsRegx = '"comment_num":(\d+),'

    # 楼中楼
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
            (kw, self.ForumListUrl.format(
                kw=kw, pn=pn * 50
            )) for kw in self.Schools for pn in range(0, self.MaxPage)
        ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        print("Process Id: ", os.getpid())
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
        if 0 <= datetime.now().hour < 9:
            self.log("0-8点不采集")
            return
        for school_name, url in self.start_urls:
            yield Request(url, meta={"school_name": school_name}, callback=self.parse_forum_list,
                          headers=Headers)

    def parse_forum_list(self, response):
        '''
        #提取帖子ID、标题、发帖人、回复数量
        '''
        self.log("parse_forum_list")
        # 获取传递过来的学校名称
        school_name = response.meta.get("school_name")
        # 获取data-field字段
        forum_data_list = response.xpath(self.ForumListXpath)
        # 正则从data里面提取帖子ID
        post_ids = forum_data_list.re(self.ForumListIdsRegx)
        item = ForumListItems(
            post_ids=post_ids,
            school_name=school_name,
            # 正则从data里面提取发帖人
            author_names=forum_data_list.re(
                self.ForumListAuthorsRegx),
            # 正则从data里面提取回复数
            reply_nums=forum_data_list.re(self.ForumListReplysRegx),
            # 提取标题
            post_titles=response.xpath(self.ForumListTitlesXpath).extract(),
            # 帖子链接
            post_urls=[self.ForumUrl.format(tid=tid) for tid in post_ids]
        )
        self.log("yield item")
        # 交给Forum Item Pipline处理
        yield item
        self.log("start get forum detail")
        for tid in post_ids:
            # 进入该帖子爬取内容和页数
            yield Request(self.ForumUrl.format(tid=tid),
                          # 这里next_page是控制对第一页数据解析后提取页数然后爬取次页
                          meta={
                              "post_id": tid,  # 帖子ID
                              "next_page": 1,  # 下一页
                              "pn": 1  # 当前页数
            },
                callback=self.parse_forum,
                headers=Headers)

    def parse_forum(self, response):
        self.log("parse_forum")
        # 当前帖子信息
        # 页数、当页主评论ID、当页主评论人、当页评论
        # 获取从上面request传递过来的当前页面帖子的ID
        post_id = response.meta.get("post_id")
        # 获取从上面request传递过来的当前页面的页数
        current_pn = response.meta.get("pn", 1)
        # 提取当页帖子页数
        page_num = response.xpath(self.ForumItemPageXpath).extract_first()
        # 提取当页评论中的data-field字段
        forum_data_list = response.xpath(self.ForumItemsXpath)
        # 从data-field中提取所有主评论的ID
        comment_ids = forum_data_list.re(self.ForumItemIdsRegx)
        # 从data-field中提取楼中楼回复页数
        lzl_comment_nums = forum_data_list.re(self.ForumItemLzlNumsRegx)
        item = ForumInfosItem(
            post_id=post_id,
            page_num=page_num,  # 页数
            comment_ids=comment_ids,
            # 从data-field中提取所有主评论人
            author_names=forum_data_list.re(self.ForumItemAuthorsRegx),
            # 评论时间
            post_times=forum_data_list.re(self.ForumItemDateRegx),
            # 评论
            post_comments=response.xpath(
                self.ForumContentsXpath).extract(),
            post_url=self.ForumNexUrl.format(tid=post_id, pn=current_pn)
        )
        # 由forum infos pipines处理入库
        yield item
        # 爬取楼中楼
        try:
            # 组合主评论ID和楼中楼数量
            for pid, nums in zip(comment_ids, lzl_comment_nums):
                if nums != "0":  # 大于0
                    # 总页数
                    lzl_total_page_num = math.ceil(
                        int(nums) / self.LzlPageSize)
                    for pn in range(1, lzl_total_page_num):
                        yield Request(
                            self.LzlUrl.format(
                                tid=post_id, pid=pid, pn=pn, t=time()),
                            meta={
                                "post_id": post_id,
                                "pid": pid,
                                "pn": current_pn
                            },
                            callback=self.parse_lzl_comment,
                            headers=Headers)
        except Exception as e:
            self.log(str(e), logging.ERROR)
        if response.meta.get("next_page", 0) and page_num:  # 判断是不是循环爬取下一页
            self.log("get next page")
            # 继续爬取帖子下一页
            try:
                page_num = int(page_num)
                if page_num < 11:  # 小于10页才继续
                    for pn in range(2, int(page_num) + 1):
                        yield Request(
                            self.ForumNexUrl.format(tid=post_id, pn=pn),
                            meta={
                                "post_id": post_id,
                                "pn": pn
                            },
                            callback=self.parse_forum,  # 调用本函数继续解析,但是不循环去抓取下一页了
                            headers=Headers)
            except Exception as e:
                self.log(str(e), logging.ERROR)

    def parse_lzl_comment(self, response):
        self.log("parse_lzl_comment")
        # 获取从上面request传递过来的当前页面的页数
        current_pn = response.meta.get("pn", 1)
        # 获取request传递过来的帖子ID
        post_id = response.meta.get("post_id", "")
        # 回复中的楼中楼评论解析
        item = LzlCommentItem(
            post_id=post_id,
            # 获取requests传递过来的主评论ID
            comment_id=response.meta.get("pid", ""),
            post_comments=response.xpath(
                self.ForumItemLzlContentsXpath).extract(),
            post_times=response.xpath(self.ForumItemLzlTimesXpath).extract(),
            author_names=response.xpath(self.ForumItemLzlsXpath).re(
                self.ForumItemLzlAuthorsRegx),
            post_url=self.ForumNexUrl.format(tid=post_id, pn=current_pn)
        )
        yield item
