# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import os,sys
from imp import reload
abspath = os.path.dirname(__file__)
print(abspath)
sys.path.append(abspath)
reload(sys)
# sys.setdefaultencoding("utf-8")       # py3取消了该用法

import web
from web import form
from model import orm
from model import model
from control import Student
from control import QuestionBackManage
from control import KnowledgePointManage
from control import StrategyManage
from control import ExamManage
from control import ScoreManage
from control import StudentManage
from control import Teacher
from control import GrobalParams
import util
import datetime
import time
from model.orm import *
import _thread
import os
import shutil
from config_default import question_source
from config_default import server_num

urls = (
    '/Login', 'Login',
    '/Student/', Student.app,
    '/Teacher/', Teacher.app,
     # 题库管理
    '/QuestionBackManage/', QuestionBackManage.app,
     # 知识点管理
    '/KnowledgePointManage/', KnowledgePointManage.app,
     # 策略管理
    '/StrategyManage', StrategyManage.app,
    # 考试管理
    '/ExamManage/', ExamManage.app,
    # 成绩管理
    '/ScoreManage/', ScoreManage.app,
     # 学生管理
    '/StudentManage/', StudentManage.app,
)

# render = web.template.render('template/')                 # 不需要使用模板

# 该方法搭建一个WebApp， urls为路由表，locals()以字典形式返回局部命名空间，因此可以通过名字来获取对象
app = web.application(urls, locals(), autoreload = True)
web.config.debug = False                                    # session的使用需要禁用调试

# session用来存储页面访问的次数，从而实现对访问次数的记录
if web.config.get("_session") is None:                      # 判断session是否存在于web.config中
    # store = web.session.DiskStore('sessions')db的一个实例化对象
    store = web.session.DBStore(orm.db, 'sessions')         # session是orm.
    '''orm.db = web.database(host=configs.db.host, port=configs.db.port, dbn='mysql', db=configs.db.database, user=configs.db.user,
    pw=configs.db.password)'''
    # session = web.session.Session(app, store, initializer={'student_id': '', "status": 1, 'ex_id': ''})    # 初始化session，并网session的字典中添加三个参数
    session = web.session.Session(app, web.session.DiskStore("session"), initializer={'student_id': '', "status": 1, 'ex_id': ''})
    web.config._session = session                           # 赋值web.config._session
else:
    session = web.config._session                           # 如果web.config中存在session,则直接赋值给session


# web.ctx用于获取客户端信息。它基于ThreadDict，他能够与线程的id相对应，多用户访问时，可以为某一特定的http请求提供数据
# 可用web.ctx操作Session(会话)
# 通过session_hook()来赋值web.ctx,使session成为全局变量，并能通过web.ctx调用
def session_hook():
    web.ctx.session = session                               # 赋值客户端session,使session成为全局变量


# 通过web.loadhook()(加载钩子)添加应用处理器来修改全局变量web.ctx
app.add_processor(web.loadhook(session_hook))


application = app.wsgifunc()        # 该函数返回一个WSGI兼容的函数，实现了URL的路由等功能。该函数目的是与WSGI应用服务器对接


class Login:
    def GET(self):
        print("app.Login")
        return "ok"


if __name__ == '__main__':
    print("app.py作为主程序")
    app.run()