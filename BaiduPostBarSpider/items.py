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
    post_ids = Field(serializer=list)  # 所有帖子ID
    author_names = Field(serializer=list)  # 所有发帖人
    reply_nums = Field(serializer=list)  # 回复数量
    post_titles = Field(serializer=list)  # 帖子标题


class ForumInfosItem(Item):
    '''
    #帖子主评论
    '''
    post_id = Field(serializer=str)  # 当前页面帖子的ID
    page_num = Field(serializer=str)  # 当前页面帖子的页数
    post_ids = Field(serializer=list)  # 所有主评论ID
    author_names = Field(serializer=list)  # 所有评论人
    post_times = Field(serializer=list)  # 回复时间
    post_contents = Field(serializer=list)  # 评论
    lzl_comment_nums = Field(serializer=list)  # 楼中楼评论数量
    post_url = Field(serializer=str)  # 帖子链接


class LzlCommentItem(Item):
    '''
    #楼中楼回复
    '''
    post_id = Field(serializer=str)  # 当前页面帖子的ID
    comment_id = Field(serializer=str)  # 当前主评论ID
    author_names = Field(serializer=list)  # 回复中的评论人
    post_times = Field(serializer=list)  # 回复时间
    post_contents = Field(serializer=list)  # 回复内容
