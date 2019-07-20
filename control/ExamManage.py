#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
from config import configs

import web
from model import model
import util
import datetime
import time
import _thread
from model.orm import *
urls = (
    '/','index',
    'delay_exam','delay_exam',
    'change_pc','change_pc',
    'stop_exam','stop_exam',
    'RestartExam','RestartExam',
    'StartExamByUser','StartExamByUser',
    'StopExamByUser','StopExamByUser',
    'deleteExam','deleteExam',
    'readExam','readExam',
    'RestartreadExam','RestartreadExam',
    'RestartsinglereadExam','RestartsinglereadExam',
    'StopExamByClass','StopExamByClass',
    'SuspendExam','SuspendExam',
    'ContinueExam','ContinueExam',
    'EmptyIP','EmptyIP',
    'recover_exam','recover_exam',
)
class index:
    def GET(self):
        mydata = web.input(name=None)
        return 'admin page'
    def POST(self):
        mydata = web.input(name=None)
        return 'admin page'


# 重做，刷新学生考试状态为未参加
class recover_exam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        information=model.Information_model.getByPK(params.in_id)
        try:
            information.in_state ='0'
            information.in_score = None
            information.in_endtime = None
            information.update()
            db.delete('exam_question', where="information_in_id = $information_in_id",
                      vars={'information_in_id': params.in_id})
        except:
            response = util.Response(status=util.Status.__error__, )
            return util.objtojson(response)
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

# 停止一个班的考试
class StopExamByClass:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        information = model.Information_model()
        information_data = information.query('SELECT * FROM information WHERE \
                    class_cl_id=%s and exam_ex_id=%s' % (params.class_cl_id, params.ex_id))
        information_data = [model.Information_model(**item) for item in information_data]
        exam = model.Exam_model.getByPK(params.ex_id)
        if exam.ex_type=="0":
            for information in information_data:
                information.in_endtime = datetime.datetime.now()
                information.in_state = '2'
                information.in_temp_ip = None
                db.update('exam_question', where="information_in_id = %s" % (information.in_id), eq_get_score='-2', )
                information.update()
            response = util.Response(status=util.Status.__success__, )
            return util.objtojson(response)
        else:
            if exam.ex_auto =="1":
                for information in information_data:
                    information.in_endtime = datetime.datetime.now()
                    if information.in_state=='1':
                        information.in_state = '2'
                        information.in_temp_ip = None
                        db.update('exam_question', where="information_in_id = %s" % (information.in_id),
                              eq_get_score='-2', )
                        information.update()
                        _thread.start_new(util.GetScore, (1,information.in_id))
            response = util.Response(status=util.Status.__success__, )
            return util.objtojson(response)

class delay_exam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        print(params)
        information=model.Information_model.getByPK(params.in_id)
        try:
            minutes = datetime.timedelta(minutes=int(params.delay_time))
            information.in_endtime += minutes
            information.update()
        except:
            response = util.Response(status=util.Status.__error__, )
            return util.objtojson(response)
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

class change_pc:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        print(params)
        information=model.Information_model.getByPK(params.in_id)
        try:
            information.in_ip =None
            information.in_temp_ip = None
            information.update()
        except:
            response = util.Response(status=util.Status.__error__, )
            return util.objtojson(response)
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

# 作弊单个停止考试
class stop_exam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        information=model.Information_model.getByPK(params.in_id)
        try:
            information.in_state ='3'
            information.in_score = 0
            information.update()
            db.update('exam_question', where="information_in_id=%s"%(params.in_id), eq_get_score=0, )
        except:
            response = util.Response(status=util.Status.__error__, )
            return util.objtojson(response)
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

# 重新考试
class RestartExam:
    def POST(self):
        params = web.input()
        web.header("Access-Control-Allow-Origin", "*")
        exam = model.Exam_model.getByPK(params.ex_id)
        exam.ex_state = '1'
        delta = exam.ex_time_end - exam.ex_time_start
        exam.ex_time_start = datetime.datetime.now()
        exam.ex_time_end = exam.ex_time_start +delta
        exam.update()
        information_data = model.Information_model.query('SELECT * FROM information WHERE \
                                    exam_ex_id=%s' % (params.ex_id))
        information_data = [model.Information_model(**items) for items in information_data]
        for information in information_data:
            information.in_state = '0'
            information.inscore = -1
            information.in_ip = None
            information.update()
            db.delete('exam_question', where="information_in_id = $information_in_id",
                      vars={'information_in_id': information.in_id, })
        response = util.Response(status=util.Status.__success__, )
        return util.objtojson(response)

class StartExamByUser:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        exam = model.Exam_model.getByPK(params.ex_id)
        exam.ex_state='1'
        exam.ex_time_start = datetime.datetime.now()
        exam.update()
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

# 停止这场考试
class StopExamByUser:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        exam = model.Exam_model.getByPK(params.ex_id)
        if exam.ex_type == '0':
            exam['ex_state'] = '4'
        else:
            # 正式考试,自动判卷,转到正在阅卷
            if exam.ex_auto == '1':
                exam['ex_state'] = '3'
                _thread.start_new(upExamStatusFour, (1, exam.ex_id))
            else:
                # 正式考试,非自动判卷,转到结束考试但成绩未出
                exam['ex_state'] = '2'
        exam.ex_time_end = datetime.datetime.now()
        exam.update()
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

# 暂停考试
class SuspendExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        exam = model.Exam_model.getByPK(params.ex_id)
        exam['ex_state'] = '5'
        exam.update()
        db.update('information', where="exam_ex_id=%s and in_state = %s" % (params.ex_id,'1'), in_state=2, )
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

# 继续考试
class ContinueExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        exam = model.Exam_model.getByPK(params.ex_id)
        exam['ex_state'] = '1'
        exam.update()
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

def upExamStatusFour(delay,ex_id):
    while 1:
        # print "four"
        time.sleep(delay)
        exam = model.Exam_model.getByPK(ex_id)
        informations = model.Information_model.getByArgs(exam_ex_id=ex_id)
        flag = 0
        for information in informations:
            information.in_score = util.upInformationScore(information.in_id)
            if information.in_score ==-1:
                flag = 1
                break
            else:
                information.update()
        if flag==0:
            exam.ex_state='4'
            exam.update()
            break

class readExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        exam = model.Exam_model.getByPK(params.ex_id)
        exam.ex_state='3'
        exam.update()
        db.update('exam_question', where="information_in_id in (select \
                 in_id from information where exam_ex_id = \
                 %s)"%(params.ex_id), eq_get_score='-2', )
        _thread.start_new(upExamStatusFour, (10, exam.ex_id))
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

# 重新阅卷
class RestartreadExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        exam = model.Exam_model.getByPK(params.ex_id)
        exam.ex_state='3'
        exam.update()
        db.update('exam_question', where="information_in_id in (select \
                 in_id from information where exam_ex_id = \
                 %s)"%(params.ex_id), eq_get_score='-2', )
        db.update('information', where="exam_ex_id = %s" % (params.ex_id), in_score='-1', )
        _thread.start_new(upExamStatusFour, (1, exam.ex_id))
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

# 重新单个学生阅卷
class RestartsinglereadExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        print(params)
        exam = model.Exam_model.getByPK(params.ex_id)
        #exam.ex_state='3'
        exam.update()
        db.update('exam_question', where="information_in_id in (select \
                 in_id from information where exam_ex_id = \
                 %s and student_st_id = %s)"%(params.ex_id,params.st_id), eq_get_score='-2', )
        db.update('information', where="exam_ex_id = %s and student_st_id = %s" % (params.ex_id,params.st_id), in_score='-1', )
        _thread.start_new(upExamStatusFour, (1, exam.ex_id))
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

class deleteExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        exam = model.Exam_model.getByPK(params.ex_id)
        db.delete('information', where="exam_ex_id = $exam_ex_id",
                  vars={'exam_ex_id': params.ex_id, })
        exam.delete()
        response = util.Response(status=util.Status.__success__,message=exam)
        return util.objtojson(response)

class EmptyIP:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        db.update('information',where="1 = 1", in_temp_ip=None,)
        response = util.Response(status=util.Status.__success__, )
        return util.objtojson(response)

app = web.application(urls,globals())
render = web.template.render('template')
if __name__ == '__main__':
    
    if len(urls)&1 == 1:
        print("urls error, the size of urls must be even.")
    else:
        app.run()
