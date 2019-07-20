#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Michael Liao'

'''
Default configurations.
'''
#
# configs = {
#     'db': {
#         'host': '127.0.0.1',
#         'port': 3306,
#         'user': 'root',
#         'password': '123456',
#         'database': 'examdb'
#     },
#     'session': {
#         'secret': 'AwEsOmE'
#     },
# }

configs = {
    'db': {
        'host': '192.168.1.69',
        'port': 3306,
        'user': 'admin',
        'password': 'EXAMhost#6636',
        'database': 'examdb'
    },
    'session': {
        'secret': 'AwEsOmE'
    },
}

# u指的是unicode编码
question_source = u'D:/Desktop/gexinghuashiyanshi/2018-11-07TEST_SYSTEM2.3/judgeFile/data'                                # u指的是unicode编码
student_source = u'D:/Desktop/gexinghuashiyanshi/2018-11-07TEST_SYSTEM2.3/WEB-System/exam/source/excel'
remind_source = u'D:/Desktop/gexinghuashiyanshi/2018-11-07TEST_SYSTEM2.3/WEB-System/exam/source'
exampage_source = u'D:/Desktop/gexinghuashiyanshi/2018-11-07TEST_SYSTEM2.3/WEB-System/exam/source/exampage'
server_num=0
'''
question_source=u'/home/judgeFile/data' #这个是判题系统需要的测试输入输出文件地址
student_source =u'/home/exam/source/excel' #这个是导入学生放置excel文件的地址
remind_source = u'/home/exam/source' #这个是学生登录提示remind.txt路径
exampage_source =u'/home/exam/source/exampage'# 导出试卷服务器存放路径
server_num=0 # 服务器编号，多个服务器需要公用一个数据库，用0,1,2...区分#具体是保证每个服务器上都有判题系统需要的测试输入输出文件，且保持统一
'''

import logging
logging_level = logging.DEBUG
