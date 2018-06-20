#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Default configurations.
'''

configs = {
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'admin',
        'password': 'EXAMhost#6636',
        'database': 'examdb'
    },
    'session': {
        'secret': 'AwEsOmE'
    },     
}
question_source=u'/home/judgeFile/data'
student_source =u'/home/exam/source/excel'
remind_source = u'/home/exam/source'
exampage_source =u'/home/exam/source/exampage'
server_num=0
import logging
logging_level = logging.DEBUG
