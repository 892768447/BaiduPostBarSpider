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

from datetime import datetime
from hashlib import md5 as MD5
from scrapy.exceptions import DropItem
from twisted.internet import reactor
from BaiduPostBarSpider.items import ForumListItems, ForumInfosItem, LzlCommentItem
from BaiduPostBarSpider.models import ForumListItemsModel,\
    ForumCommentItemsModel


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

    def insertData(self, item):
        # 数据库session
        session = self.Session()
        school_name = item.get("school_name", "")  # 学习名称
        for post_id, post_title, author_name, reply_num, post_url in zip(
            item.get("post_ids", []),
            item.get("post_titles", []),
            item.get("author_names", []),
            item.get("reply_nums", []),
            item.get("post_urls", [])
        ):
            model = ForumListItemsModel(
                post_id=post_id,
                school_name=school_name,
                post_title=post_title,
                author_name=author_name.encode().decode(
                    "unicode_escape") if author_name.find(
                        r"\u") > -1 else author_name,  # 把\\u 转成中文
                reply_num=reply_num,
                post_url=post_url
            )
            session.merge(model)  # 存在则更新,不存在则插入
        session.commit()  # 批量提交
        session.close()

    def process_item(self, item, spider):
        if isinstance(item, ForumListItems):
            reactor.callInThread(self.insertData, item)  # @UndefinedVariable
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

    def insertData(self, item):
        # 数据库session
        session = self.Session()
        post_id = item.get("post_id", "")  # 帖子ID
        post_url = item.get("post_url", "")  # 帖子链接
        for comment_id, author_name, post_time, post_comment in zip(
            item.get("comment_ids", []),  # 主评论ID
            item.get("author_names", []),
            item.get("post_times", datetime.now()),  # 评论时间
            item.get("post_comments", [])
        ):
            # 生成唯一索引
            data = post_id + comment_id + author_name + post_time + post_comment
            md5 = MD5(data.encode())
            model = ForumCommentItemsModel(
                md5_key=md5.hexdigest(),
                post_id=post_id,
                comment_id=comment_id,
                author_name=author_name.encode().decode(
                    "unicode_escape") if author_name.find(
                        r"\u") > -1 else author_name,  # 把\\u 转成中文
                post_time=post_time,
                post_comment=post_comment.strip(),
                post_url=post_url + \
                "&pid={0}#{0}".format(comment_id)  # 直接跳转到该楼层
            )
            session.merge(model)  # 存在则更新,不存在则插入
        session.commit()  # 批量提交
        session.close()

    def process_item(self, item, spider):
        if isinstance(item, ForumInfosItem):
            reactor.callInThread(self.insertData, item)  # @UndefinedVariable
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

    def insertData(self, item):
        # 数据库session
        session = self.Session()
        post_id = item.get("post_id", "")  # 帖子ID
        comment_id = item.get("comment_id", "")  # 当前主评论ID
        post_url = item.get("post_url", "")  # 帖子链接
        for author_name, post_time, post_comment in zip(
            item.get("author_names", []),
            item.get("post_times", datetime.now()),  # 评论时间
            item.get("post_comments", [])
        ):
            # 生成唯一索引
            data = post_id + comment_id + author_name + post_time + post_comment
            md5 = MD5(data.encode())
            model = ForumCommentItemsModel(
                md5_key=md5.hexdigest(),
                post_id=post_id,
                comment_id=comment_id,
                author_name=author_name.encode().decode(
                    "unicode_escape") if author_name.find(
                        r"\u") > -1 else author_name,  # 把\\u 转成中文
                post_time=post_time,
                post_comment=post_comment.strip(),
                post_url=post_url + \
                "&pid={0}#{0}".format(comment_id)  # 直接跳转到该楼层
            )
            session.merge(model)  # 存在则更新,不存在则插入
        session.commit()  # 批量提交
        session.close()

    def process_item(self, item, spider):
        if isinstance(item, LzlCommentItem):
            reactor.callInThread(self.insertData, item)  # @UndefinedVariable
            raise DropItem("this LzlCommentItem into db ok")
        return item
