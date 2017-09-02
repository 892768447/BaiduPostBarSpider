#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017年8月28日
@author: Irony."[讽刺]
@site: http://alyl.vip, http://orzorz.vip, https://coding.net/u/892768447, https://github.com/892768447
@email: 892768447@qq.com
@file: pipelines
@description: 
'''

from scrapy.exceptions import DropItem

from BaiduPostBarSpider.items import ForumListItems, ForumInfosItem, LzlCommentItem
from BaiduPostBarSpider.models import ForumModel  # @UnresolvedImport


# @UnresolvedImport
__Author__ = "By: Irony.\"[讽刺]\nQQ: 892768447\nEmail: 892768447@qq.com"
__Copyright__ = "Copyright (c) 2017 Irony.\"[讽刺]"
__Version__ = "Version 1.0"


class ForumListItemsPipeline(object):
    '''
    #百度贴吧帖子列表数据处理
    '''

    def __init__(self, Session):
        self.Session = Session

    @classmethod
    def from_crawler(cls, crawler):
        return cls(Session=crawler.settings.Session)

    def process_item(self, item, spider):
        if isinstance(item, ForumListItems):
            print("ForumListItems: ", ForumListItems)
            raise DropItem("this ForumListItems into db ok")
        return item


class ForumInfosItemPipeline(object):
    '''
    #帖子主评论数据处理
    '''

    def __init__(self, Session):
        self.Session = Session

    @classmethod
    def from_crawler(cls, crawler):
        return cls(Session=crawler.settings.Session)

    def process_item(self, item, spider):
        if isinstance(item, ForumInfosItem):
            print("ForumInfosItem: ", ForumInfosItem)
            raise DropItem("this ForumInfosItem into db ok")
        return item


class LzlCommentItemPipeline(object):
    '''
    #楼中楼回复数据处理
    '''

    def __init__(self, Session):
        self.Session = Session

    @classmethod
    def from_crawler(cls, crawler):
        return cls(Session=crawler.settings.Session)

    def process_item(self, item, spider):
        if isinstance(item, LzlCommentItem):
            print("LzlCommentItem: ", LzlCommentItem)
            raise DropItem("this LzlCommentItem into db ok")
        return item
