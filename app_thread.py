# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import os, sys

abspath = os.path.dirname(__file__)

from model import model
import util
import datetime
import time
from model.orm import db
import threading
import thread
import shutil
from config_default import question_source
from config_default import server_num

def upExamQuestionState(delay):
    while (1):
        # print threadName
        time.sleep(delay)
        db.update('exam_question', where="eq_get_score = '-3'", eq_get_score='-2', )

def upExamStatusStart(delay):
    while (1):
        # print threadName
        time.sleep(delay)
        startExam = dict(ex_state=0)
        examModel = model.Exam_model()
        # 未开始的考试
        exams = examModel.getByArgs(**startExam)
        for exam in exams:
            if exam['ex_time_start'] < datetime.datetime.now():
                exam['ex_state'] = '1'
                exam.update()


def upExamStatusFour(delay, ex_id):
    while 1:
        time.sleep(delay)
        # print "four"
        exam = model.Exam_model.getByPK(ex_id)
        informations = model.Information_model.getByArgs(exam_ex_id=ex_id)
        flag = 0
        for information in informations:
            information.in_score = util.upInformationScore(information.in_id)
            if information.in_score == -1:
                flag = 1
                break
            else:
                information.update()
        if flag == 0:
            exam.ex_state = '4'
            exam.update()
            break


def upExamStatusStop(delay):
    while (1):
        # print threadName
        time.sleep(delay)
        startExam = dict(ex_state=1)
        examModel = model.Exam_model()
        # 正在考试的考试
        exams = examModel.getByArgs(**startExam)
        for exam in exams:
            # 可能变成2,3,4
            # 练习模式考试直接出成绩
            if exam.ex_type == '0':
                if exam['ex_time_end'] < datetime.datetime.now():
                    exam['ex_state'] = '4'
                    exam.update()
            else:
                # 正式考试,自动判卷,转到正在阅卷
                if exam.ex_auto == '1':
                    if exam['ex_time_end'] < datetime.datetime.now():
                        exam['ex_state'] = '3'
                        thread.start_new(upExamStatusFour, (1, exam.ex_id))
                        exam.update()
                else:
                    # 正式考试,非自动判卷,转到结束考试但成绩未出
                    if exam['ex_time_end'] < datetime.datetime.now():
                        exam['ex_state'] = '2'
                        exam.update()


def upInformationState(delay):
    while (1):
        # print threadName

        time.sleep(delay)
        startExam = dict(in_state=1)
        # 正在考试的学生
        information = model.Information_model.getByArgs(**startExam)
        delta = datetime.timedelta(minutes=1)
        for item in information:
            if item['in_endtime'] < datetime.datetime.now() - delta:
                item['in_state'] = '2'
                item['in_temp_ip'] = None
                item.update()
                util.SaveFillb(item['in_id'])
                db.update('exam_question', where="information_in_id = %s" % (item['in_id']), eq_get_score='-2', )
                thread.start_new(util.GetScore, (1, item['in_id']))


def CreatQuestionSource(delay):
    while (1):
        time.sleep(delay)
        try:
            num = int(10 ** server_num)
            question = model.Question_model.query('select * from question where qt_state div %s %% 10 = 0' % (num))
            # question = model.Question_model.getByArgs(qt_state=0)
            question = [model.Question_model(**item) for item in question]
            for item in question:
                if item.qt_type == 'coding':
                    coding = model.Coding_model.getByPK(item.qt_id)
                    if os.path.exists('%s/%s' % (question_source, item.qt_id)):
                        shutil.rmtree('%s/%s' % (question_source, item.qt_id))
                    os.mkdir('%s/%s' % (question_source, item.qt_id))
                    item.qt_state += num
                    item.update()
                    test_in = coding.co_test_answer_in.split('&&&')
                    test_out = coding.co_test_answer_out.split('&&&')
                    # print len(test_in)
                    for k in range(1, len(test_in) - 1):
                        with open('%s/%s/%s.in' % (question_source, coding.question_qt_id, k), 'w') as f:
                            f.write(test_in[k])
                        with open('%s/%s/%s.out' % (question_source, coding.question_qt_id, k), 'w') as f:
                            f.write("%s" % test_out[k])
                elif item.qt_type == 'fillb':
                    Fillb = model.Fillb_model.getByPK(item.qt_id)
                    if os.path.exists('%s/%s' % (question_source, item.qt_id)):
                        shutil.rmtree('%s/%s' % (question_source, item.qt_id))
                    os.mkdir('%s/%s' % (question_source, item.qt_id))
                    item.qt_state += num
                    item.update()
                    test_in = Fillb.fb_test_answer_in.split('&&&')
                    test_out = Fillb.fb_test_answer_out.split('&&&')
                    for k in range(1, len(test_in) - 1):
                        # with open('../examTransplant1.7/source/question/%s/%s.in' % (Fillb.question_qt_id, k), 'w') as f:
                        with open('%s/%s/%s.in' % (question_source, Fillb.question_qt_id, k), 'w') as f:
                            f.write(test_in[k])
                        with open('%s/%s/%s.out' % (question_source, Fillb.question_qt_id, k), 'w') as f:
                            f.write("%s" % test_out[k])
        except BaseException as e:
            with open('/home/exam/log.txt', 'a+') as f:
                f.write(e)
# thread.start_new(upExamStatusStart, ("thread-1", 1,))
# thread.start_new(upExamStatusStop, ("thread-2", 1,))
# thread.start_new(upInformationState, ("thread-3", 1,))
# thread.start_new(CreatQuestionSource, ("thread-4", 1,))


# if __name__ == '__main__':
#     thread.start_new(upExamStatusStart, ("thread-1", 1,))
#     thread.start_new(upExamStatusStop, ("thread-2", 1,))
#     thread.start_new(upInformationState, ("thread-3", 1,))
#     thread.start_new(CreatQuestionSource, ("thread-4", 1,))
# thread.start_new(app.run())

threads = []
threads.append(threading.Thread(target=upExamStatusStart, args=(1,)))
threads.append(threading.Thread(target=upExamStatusStop, args=(1,)))
threads.append(threading.Thread(target=upInformationState, args=(1,)))
threads.append(threading.Thread(target=CreatQuestionSource, args=(1,)))
threads.append(threading.Thread(target=upExamQuestionState, args=(1000,)))

if __name__ == '__main__':
    for t in threads:
        # t.setDaemon(True)
        t.start()
