#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017年8月28日
@author: Irony."[讽刺]
@site: http://alyl.vip, http://orzorz.vip, https://coding.net/u/892768447, https://github.com/892768447
@email: 892768447@qq.com
@file: items
@description: 
'''

from scrapy.item import Item, Field


__Author__ = "By: Irony.\"[讽刺]\nQQ: 892768447\nEmail: 892768447@qq.com"
__Copyright__ = "Copyright (c) 2017 Irony.\"[讽刺]"
__Version__ = "Version 1.0"

class ForumListItems(Item):
    '''
    #百度贴吧帖子列表
    '''
    post_ids = Field(serializer=list)#所有帖子ID
    author_names = Field(serializer=list)#所有发帖人
    reply_nums = Field(serializer=list)#回复数量
    post_titles = Field(serializer=str)#帖子标题


class ForumInfosItem(Item):
    '''
    #帖子评论
    '''
    post_id = Field(serializer=str)  # 当前页面帖子的ID
    post_title = Field(serializer=str)  # 当前页面帖子的标题
    page_num = Field(serializer=str)  # 当前页面帖子的页数
    post_content = Field(serializer=str)  # 评论
    data_field = Field(serializer=str)  # 当前页面帖子的data字段

class LzlCommentItem(Item):
    '''
    #楼中楼回复
    '''
    post_id = Field(serializer=str)  # 当前页面帖子的ID
    post_content = Field(serializer=str)  # 回复内容
    post_time = Field(serializer=str)  # 回复时间
    data_field = Field(serializer=str)  # 回复中的data字段
    