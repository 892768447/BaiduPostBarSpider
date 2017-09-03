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
from BaiduPostBarSpider.models import ForumListItemsModel
from datetime import datetime


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
            # 数据库session
            session = self.Session()
            for post_id, post_title, author_name, reply_num in zip(
                item.get("post_ids", []),
                item.get("post_titles", []),
                item.get("author_names", []),
                item.get("reply_nums", [])
            ):
                model = ForumListItemsModel(
                    post_id=post_id,
                    post_title=post_title,
                    author_name=author_name.encode().decode("unicode_escape") \
                        if author_name.find(r"\u") > -1 else author_name,  # 把\\u 转成中文
                    reply_num=reply_num
                )
                session.merge(model)  # 存在则更新,不存在则插入
            session.commit()  # 批量提交
            session.close()
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
            # 数据库session
            session = self.Session()
            post_id = item.get("post_id", "")  # 帖子ID
            for comment_id, author_name, post_content, post_time in zip(
                item.get("post_ids", []),  # 主评论ID
                item.get("author_names", []),
                item.get("post_contents", []),
                item.get("post_times", datetime.now())  # 评论时间
            ):
                model = ForumListItemsModel(
                    post_id=post_id,
                    comment_id=comment_id,
                    author_name=author_name.encode().decode("unicode_escape") \
                        if author_name.find(r"\u") > -1 else author_name,  # 把\\u 转成中文
                    post_content=post_content,
                    post_time=post_time
                )
                session.merge(model)  # 存在则更新,不存在则插入
            session.commit()  # 批量提交
            session.close()
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
            # 数据库session
            session = self.Session()
            post_id = item.get("post_id", "")  # 帖子ID
            for comment_id, author_name, post_content, post_time in zip(
                item.get("post_ids", []),  # 主评论ID
                item.get("author_names", []),
                item.get("post_contents", []),
                item.get("post_times", datetime.now())  # 评论时间
            ):
                model = ForumListItemsModel(
                    post_id=post_id,
                    comment_id=comment_id,
                    author_name=author_name.encode().decode("unicode_escape") \
                        if author_name.find(r"\u") > -1 else author_name,  # 把\\u 转成中文
                    post_content=post_content,
                    post_time=post_time
                )
                session.merge(model)  # 存在则更新,不存在则插入
            session.commit()  # 批量提交
            session.close()
            raise DropItem("this LzlCommentItem into db ok")
        return item
