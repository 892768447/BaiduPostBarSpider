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

import json

from scrapy.exceptions import DropItem

from BaiduPostBarSpider.items import ForumListItem, ForumTitleItem  # @UnresolvedImport
from BaiduPostBarSpider.models import ForumModel  # @UnresolvedImport


__Author__ = "By: Irony.\"[讽刺]\nQQ: 892768447\nEmail: 892768447@qq.com"
__Copyright__ = "Copyright (c) 2017 Irony.\"[讽刺]"
__Version__ = "Version 1.0"


class ForumListItemPipeline(object):
    '''
    #百度爬虫首页帖子列表数据处理
    '''

    def __init__(self, Session):
        self.Session = Session

    @classmethod
    def from_crawler(cls, crawler):
        return cls(Session=crawler.settings.Session)
#         return cls(Session=crawler.settings.get("Session"))

    def process_item(self, item, spider):
        if isinstance(item, ForumTitleItem):
            session = self.Session()  # 更新标题
            forum = ForumModel(
                post_id=item.get("post_id", "").split("?")[0],
                post_title=item.get("post_title", "")
            )
            session.merge(forum)  # 存在则更新,不存在则插入
            session.commit()  # 提交
            session.close()
            raise DropItem("update title ok")
        elif isinstance(item, ForumListItem):
            # 数据库入库
            session = self.Session()
            for data in item.get("data_field", []):  # 解析数据
                try:
                    data = json.loads(data)  # 尝试解析为json
                except:
                    continue
                post_id = str(data.get("id", "")).split("?")[0]
                author_name = data.get("author_name", "")
                reply_num = data.get("reply_num", "")
                if not post_id:
                    continue
                forum = ForumModel(
                    post_id=post_id,
                    author_name=author_name,
                    reply_num=reply_num
                )
                session.merge(forum)  # 存在则更新,不存在则插入
            session.commit()  # 批量提交
            session.close()
            raise DropItem("this item into db ok")
        return item
