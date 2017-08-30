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

from BaiduPostBarSpider.items import ForumListItem  # @UnresolvedImport
from BaiduPostBarSpider.models import ForumModel


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
        if isinstance(item, ForumListItem):
            if item.isNull():
                raise DropItem("this item is null")
            # 数据库入库
            session = self.Session()
            user = ForumModel(**item)
            session.merge(user)
            session.commit()
            session.close()
            raise DropItem("this item into db ok")
        return item
