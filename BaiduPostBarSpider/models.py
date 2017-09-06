#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017年8月30日
@author: Irony."[讽刺]
@site: alyl.vip, orzorz.vip, irony.coding.me , irony.iask.in , mzone.iask.in
@email: 892768447@qq.com
@file: BaiduPostBarSpider.models
@description: 数据库表映射
'''
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP, Text, DateTime
from datetime import datetime


__version__ = "0.0.1"

Base = declarative_base()


class ForumListItemsModel(Base):

    # 表名
    __tablename__ = "Forum_List_Items".lower()
    # 表结构
    post_id = Column(String(20), primary_key=True, doc="帖子ID")
    school_name = Column(String(20), primary_key=True, doc="帖子ID")
    post_title = Column(String(255), doc="帖子标题")
    author_name = Column(String(255), doc="发帖人")
    reply_num = Column(Integer(), doc="回复数量")
    post_url = Column(Text, doc="帖子链接")
    store_time = Column(TIMESTAMP, server_default=text(
        "CURRENT_TIMESTAMP"), doc="储存时间")


class ForumCommentItemsModel(Base):

    # 表名
    __tablename__ = "Forum_Comment_Items".lower()
    # 表结构
    # md5 key 防止评论内容更新合并中由于主键的问题导致所有合并
    md5_key = Column(String(32), primary_key=True, doc="唯一值")
    post_id = Column(String(20), doc="帖子ID")
    comment_id = Column(String(20), doc="评论条目的ID")
    author_name = Column(String(255), doc="评论人")
    post_time = Column(DateTime, default=datetime.now, doc="评论时间")
    post_comment = Column(Text, doc="评论内容")
    post_url = Column(Text, doc="评论链接地址")


def dbInit():
    engine = create_engine("mysql+pymysql://root:aj1@msmobile@127.0.0.1")
    # 创建数据库
    with engine.connect() as con:
        con.execute(
            "CREATE DATABASE IF NOT EXISTS baidupostbar CHARACTER SET utf8;")
    engine = create_engine(
        "mysql+pymysql://root:aj1@msmobile@127.0.0.1/baidupostbar?charset=utf8",
        isolation_level="READ UNCOMMITTED",
        pool_size=16)  # 16个线程
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
