#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import util
import time
sys.path.append('../')
from config import configs
from model import model
from model import orm
import os
import web
import datetime
import shutil
from config_default import question_source
from config_default import exampage_source
urls = (
    '/','index',
    'AddQuestionBack/','AddQuestionBack',
    'ManageQuestionBack/','ManageQuestionBack',
    'UpdateQuestionBack/','UpdateQuestionBack',
    'ConfirmDeleteQuestionBack/','ConfirmDeleteQuestionBack',
    'OpenQuestionBack/','OpenQuestionBack',
    'RequestQuestionBack/','RequestQuestionBack',
    'AddQuestion/','AddQuestion',
    'CheckQuestion/','CheckQuestion',
    'UpdataQuestion/','UpdataQuestion',
    'SelectQuestion/','SelectQuestion',
    'BatchAddQuestion/','BatchAddQuestion',
    'DeleteQuestion/','DeleteQuestion',
    '/saveChoice/','saveChoice',
    'FuzzySearch/','FuzzySearch',
    'FiltrationQuestion/','FiltrationQuestion',
    'QuestionPrint/','QuestionPrint',
    'Getlang/', 'Getlang',
)


class index:
    def GET(self):
        mydata = web.input(name=None)
        return 'uestionbackManage page'
    def POST(self):
        mydata = web.input(name=None)
        return 'QuestionbackManage page'


# 添加题库
class AddQuestionBack:
    def GET(self):
        return 'AddQuestionBack'
    def POST(self):
        mydata = web.input()
        print("添加题库", mydata)
        qb = model.Questions_bank_model()
        must_params = qb.__notnull__
        web.header("Access-Control-Allow-Origin", "*")                      # 跨域访问
        if(util.paramsok(must_params, mydata) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            qb = model.Questions_bank_model(**mydata)
            if qb.insert():
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)


# 查询题库
class ManageQuestionBack:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*") 
        mydata = web.input()
        # must_params =set({'currentPage'})
        must_params =set({})
        if(util.paramsok(must_params, mydata) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            qb = model.Questions_bank_model()
            count = qb.count()
            reasurt = qb.getByPage(int(mydata.currentPage)-1)
            print("查询结果", reasurt)
            page = util.Page(data = reasurt, totalRow = count, currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = "未知")
            response = util.Response(status=util.Status.__success__,body=page)
            print("查询题库：", util.objtojson(response))
            return util.objtojson(response)


# 修改题库
class UpdateQuestionBack:
    def POST(self):
        mydata = web.input()
        qb = model.Questions_bank_model()
        must_params = qb.__notnull__
        web.header("Access-Control-Allow-Origin", "*") 
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            qb = model.Questions_bank_model(**mydata)
            if qb.update():
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)

# 确认删除题库
class ConfirmDeleteQuestionBack:
    def POST(self):
        mydata = web.input()
        print("删除题库", mydata)
        qb = model.Questions_bank_model()
        must_params = set (['qb_id'])
        web.header("Access-Control-Allow-Origin", "*")
        session = web.ctx.session
        # util.getFileRotatingLog().debug(session.password)           # 写入到log文件
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        elif str(mydata.deletepassword) == session.password:
            qb.qb_id = mydata.qb_id
            result = model.Questions_bank_has_question_model.getByArgs( \
                questions_bank_qb_id = qb.qb_id)
            for item in result:
                questions_bank_has_question = model.Questions_bank_has_question_model()
                questions_bank_has_question.qbhq_id = item.qbhq_id
                questions_bank_has_question.delete()

            if qb.delete():
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__,message = "删除失败")
                return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__error__, message="密码错误")
            return util.objtojson(response)
        response = util.Response(status=util.Status.__error__,message = "删除失败")
        return util.objtojson(response)


# 查看题库
class OpenQuestionBack:
    def POST(self):
        mydata = web.input()
        print("查看题目:",mydata)
        # 必须有的参数
        must_params =set({'questions_bank_qb_id','currentPage'})
        web.header("Access-Control-Allow-Origin", "*")
        currentPage = int(mydata.currentPage)-1;
        if(util.paramsok(must_params,mydata) == 2):
            print(333)
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            question = model.Question_model()
            # result = orm.db.query('select * from question where qt_id in (select question_qt_id from questions_bank_has_question where questions_bank_qb_id = %s ) order by qt_id limit %s,%s'%(int(mydata.questions_bank_qb_id),currentPage*10,currentPage*10+9))
            result = orm.db.query('select * from question where qt_id in \
                (select question_qt_id from questions_bank_has_question where questions_bank_qb_id = %s )\
                order by qt_id limit %s,%s'%(mydata.questions_bank_qb_id,currentPage*10,10))
            
            questionlist = []
            result = [model.Question_model(**item) for item in result ]
            # print result
            count = dict()
            total_num= question.query('select count(*) from question where qt_id in (select question_qt_id \
                from questions_bank_has_question where questions_bank_qb_id = %s )'%(mydata.questions_bank_qb_id))
            # print result1[0]
            choice_num = question.query('select count(*) from question where qt_id in (select question_qt_id \
                            from questions_bank_has_question where questions_bank_qb_id = %s ) and qt_type = \'choice\'' % (
                    mydata.questions_bank_qb_id))
            coding_num = question.query('select count(*) from question where qt_id in (select question_qt_id \
                                        from questions_bank_has_question where questions_bank_qb_id = %s ) and qt_type = \'coding\'' % (
                mydata.questions_bank_qb_id))
            filla_num = question.query('select count(*) from question where qt_id in (select question_qt_id \
                                                    from questions_bank_has_question where questions_bank_qb_id = %s ) \
                                                     and qt_type = \'filla\'' % (mydata.questions_bank_qb_id))
            fillb_num = question.query('select count(*) from question where qt_id in (select question_qt_id \
                                                                from questions_bank_has_question where questions_bank_qb_id = %s ) \
                                                                 and qt_type = \'fillb\'' % (mydata.questions_bank_qb_id))
            judge_num = question.query('select count(*) from question where qt_id in (select question_qt_id \
                                                                from questions_bank_has_question where questions_bank_qb_id = %s ) \
                                                                 and qt_type = \'judge\'' % (mydata.questions_bank_qb_id))
            count['total_num'] = total_num[0]['count(*)']
            count['choice_num'] = choice_num[0]['count(*)']
            count['coding_num'] = coding_num[0]['count(*)']
            count['filla_num'] = filla_num[0]['count(*)']
            count['fillb_num'] = fillb_num[0]['count(*)']
            count['judge_num'] = judge_num[0]['count(*)']
            #util.getFileRotatingLog().debug(count)
            for params in result:
                qt = params
                qt['qt_type']=util.type[qt.qt_type]
                Knowledge = model.Knowledge_model()
                KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id) 
                qt['kl_name'] = KnowledgeData.kl_name 
                questionlist.append(qt)
            # response = util.Response(status=util.Status.__success__,body = questionlist)
            # return util.objtojson(response)
            page = util.Page(data = questionlist, totalRow = int(count['total_num']), currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = count)
            response = util.Response(status=util.Status.__success__,body=page)
            print("返回信息： ", util.objtojson(response))
            return util.objtojson(response)


# 返回题库和知识点信息
class RequestQuestionBack:
    def GET(self):
        print(RequestQuestionBack)
        mydata = web.input()
        web.header("Access-Control-Allow-Origin", "*")
        Knowledge = model.Knowledge_model()
        KnowledgeData = Knowledge.getByArgs()
        questionback = model.Questions_bank_model()
        questionbackData = questionback.getByArgs()
        data = []
        data.append(KnowledgeData)
        data.append(questionbackData)
        response = util.Response(status=util.Status.__success__,body=data)
        print("返回题库和知识点信息", util.objtojson(response))
        return util.objtojson(response)


# 添加题目
class AddQuestion:
    '''更新：2018-8-24  更新添加字段qt_lang = qb_lang'''
    def POST(self):
        mydata = web.input()
        print(mydata)
        # print mydata['qt_stem'].encode("utf-8")
        qt = model.Question_model()
        web.header("Access-Control-Allow-Origin", "*")
        qbhq = model.Questions_bank_has_question_model()
        qb = model.Questions_bank_model()
        print(mydata['questions_bank_qb_id'])
        qb = qb.getByArgs(qb_id = mydata['questions_bank_qb_id'])
        # print(qb)
        # print(qb[0]['qb_lang'])
        mydata['qt_lang'] = qb[0]['qb_lang']
        # print("更新后的mydata: ", mydata)
        must_params = qt.__notnull__
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            qt = model.Question_model(**mydata)
            if mydata.qt_type == 'choice':
                choice = model.Choice_model(**mydata)
                with orm.db.transaction():
                    qt.insert()
                    reasurt = qt.query('select max(qt_id) from question')
                    choice.question_qt_id = int(reasurt[0]['max(qt_id)'])
                    choice.insert()
                    qbhq.question_qt_id = choice.question_qt_id
                    qbhq.questions_bank_qb_id = mydata.questions_bank_qb_id
                    qbhq.insert()
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)

            # 编程题加题时需要把题目先加入到exam_question表，判题系统取出题目进行判题，如果判题成功则加入到question表
            elif mydata.qt_type == 'coding':
                # qb = model.Questions_bank_model()
                # print(mydata['questions_bank_qb_id'])
                # qb = qb.getByArgs(qb_id=mydata['questions_bank_qb_id'])
                #mydata['eq_lang'] = qb[0]['qb_lang']
                #print("更改后的mydata",mydata)
                coding = model.Coding_model(**mydata)                       # 实例化一个编程题
                with orm.db.transaction():
                    qt.insert()                                             # 插入到question表
                    reasurt = qt.query('select max(qt_id) from question')
                    coding.question_qt_id = reasurt[0]['max(qt_id)']
                    qt.qt_id=coding.question_qt_id
                    coding.insert()                                         # 插入到coding表
                    qbhq.question_qt_id = coding.question_qt_id
                    qbhq.questions_bank_qb_id = mydata.questions_bank_qb_id
                    result = qbhq.insertBackid()                            # 插入到qbhd表
                    qbhq.qbhq_id = result[0]['max(qbhq_id)']
                # os.mkdir('%s/%s'%(question_source,coding.question_qt_id))
                # test_in = coding.co_test_answer_in.split('&&&')
                # test_out = coding.co_test_answer_out.split('&&&')
                # for k in range(1, len(test_in) - 1):
                #     with open('%s/%s/%s.in' % (question_source,coding.question_qt_id,k), 'w') as f:
                #         f.write(test_in[k])
                #     with open('%s/%s/%s.out' % (question_source,coding.question_qt_id,k), 'w') as f:
                #         f.write("%s"%test_out[k])
                exam_question = model.Exam_question_model()                 # 实例化exam_question表
                exam_question.information_in_id = 1
                exam_question.qt_id = qbhq.question_qt_id
                exam_question.eq_qt_type = 'coding'
                exam_question.eq_pre_score = 100
                exam_question.eq_get_score = '-2'                           # -2为待判题状态
                exam_question.eq_answer = coding.co_test_coding
                exam_question.eq_lang = qb[0]['qb_lang']
                result = exam_question.insertBackid()                       # 插入到exam_question表
                eq_id = result[0]['max(eq_id)']
                for i in range(60):                                         # 判题最大时长为1分钟
                    time.sleep(1)
                    exam_question = model.Exam_question_model.getByPK(eq_id)
                    if exam_question.eq_get_score ==100:                    # 判题成功，判题系统将该字段变为100
                        response = util.Response(status=util.Status.__success__)
                        return util.objtojson(response)
                    if exam_question.eq_get_score ==0 or i == 59:           # 判题失败时删除改题目的所有信息
                        exam_question.delete()
                        qbhq.delete()
                        coding.delete()
                        qt.delete()
                        response = util.Response(status=util.Status.__error__)
                        return util.objtojson(response)
            elif mydata.qt_type == 'filla':
                Filla = model.Filla_model(**mydata)
                with orm.db.transaction():
                    qt.insert()
                    reasurt = qt.query('select max(qt_id) from question')
                    Filla.question_qt_id = reasurt[0]['max(qt_id)']

                    Filla.insert()
                    qbhq.question_qt_id = Filla.question_qt_id
                    qbhq.questions_bank_qb_id = mydata.questions_bank_qb_id
                    qbhq.insert()
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)

            # 程序填空题加题时需要把题目先加入到exam_question表，判题系统取出题目进行判题，如果判题成功则加入到question表
            elif mydata.qt_type == 'fillb':
                Fillb = model.Fillb_model(**mydata)
                with orm.db.transaction():
                    Fillb.question_qt_id=qt.qt_id=qt.insertBackid()[0]['max(qt_id)']
                    Fillb.insert()
                    qbhq.question_qt_id = Fillb.question_qt_id
                    qbhq.questions_bank_qb_id = mydata.questions_bank_qb_id
                    result = qbhq.insertBackid()
                    qbhq.qbhq_id = result[0]['max(qbhq_id)']
                # os.mkdir('%s/%s' % (question_source,Fillb.question_qt_id))
                # test_in = Fillb.fb_test_answer_in.split('&&&')
                # test_out = Fillb.fb_test_answer_out.split('&&&')
                # for k in range(1, len(test_in) - 1):
                #     # with open('../examTransplant1.7/source/question/%s/%s.in' % (Fillb.question_qt_id, k), 'w') as f:
                #     with open('%s/%s/%s.in' % (question_source,Fillb.question_qt_id, k), 'w') as f:
                #         f.write(test_in[k])
                #     with open('%s/%s/%s.out' % (question_source,Fillb.question_qt_id, k), 'w') as f:
                #         f.write("%s" % test_out[k])
                exam_question = model.Exam_question_model()
                exam_question.information_in_id = 1
                exam_question.qt_id = qbhq.question_qt_id
                exam_question.eq_qt_type = 'fillb'
                exam_question.eq_pre_score = 100
                exam_question.eq_get_score = '-2'
                exam_question.eq_answer = Fillb.fb_pre_coding
                exam_question.eq_lang = qb[0]['qb_lang']
                exam_question.fillb_coding = Fillb.fb_pre_coding.replace('&&&',' ')
                # util.getFileRotatingLog().debug(exam_question.fillb_coding)              #写入到log文件
                result = exam_question.insertBackid()
                eq_id = result[0]['max(eq_id)']
                for i in range(60):
                    time.sleep(1)
                    exam_question = model.Exam_question_model.getByPK(eq_id)
                    if exam_question.eq_get_score == 100:
                        response = util.Response(status=util.Status.__success__)
                        return util.objtojson(response)
                    if exam_question.eq_get_score == 0 or i == 59:
                        exam_question.delete()
                        qbhq.delete()
                        Fillb.delete()
                        qt.delete()
                        response = util.Response(status=util.Status.__error__)
                        return util.objtojson(response)
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            elif mydata.qt_type == 'judge':
                Judge = model.Judge_model(**mydata)
                # print qt
                with orm.db.transaction():
                    qt.insert()
                    reasurt = qt.query('select max(qt_id) from question')
                    Judge.question_qt_id = reasurt[0]['max(qt_id)']
                    Judge.insert()
                    qbhq.question_qt_id = Judge.question_qt_id
                    qbhq.questions_bank_qb_id = mydata.questions_bank_qb_id
                    qbhq.insert()
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)                             # 返回一个对象，status = 1


# 查看题目
class CheckQuestion:
    def POST(self):
        mydata = web.input()
        qt = model.Question_model()
        kp = model.Knowledge_model()
        must_params = set (['qt_id'])
        web.header("Access-Control-Allow-Origin", "*") 
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            qt = model.Question_model(**mydata)
            questiondata = qt.getByArgs(qt_id = qt.qt_id)
            KnowledgeData = kp.getByArgs(kl_id = questiondata[0]['knowledge_kl_id'])
            qt_typedata = orm.db.query('select * from %s where question_qt_id = %s'%(questiondata[0].qt_type,qt.qt_id))
            result1 = [model.Question_model(**item) for item in qt_typedata ]
            data = []
            data.append(questiondata)
            data.append(KnowledgeData)
            data.append(result1)
            response = util.Response(status=util.Status.__success__,body = data)
            return util.objtojson(response)


# 修改题目
class UpdataQuestion:
    def POST(self):
        mydata = web.input();
        print("修改题目", mydata)
        qt = model.Question_model()
        recover_question = model.Question_model.getByPK(mydata.qt_id)
        recover_coding = model.Coding_model.getByPK(mydata.qt_id)
        recover_fillb = model.Fillb_model.getByPK(mydata.qt_id)
        kp = model.Knowledge_model()
        web.header("Access-Control-Allow-Origin", "*")
        must_params = set({'qt_id','qt_type','qt_stem','kl_name','qb_id','eq_lang'})
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            knowlagedata = kp.getByArgs(kl_name = mydata.kl_name)
            qt = model.Question_model(**mydata)
            qt.knowledge_kl_id = knowlagedata[0].kl_id
            qt.qt_state=0
            qt.update()
            if mydata.qt_type == 'choice':
                choice = model.Choice_model(**mydata)
                choice.question_qt_id = qt.qt_id
                choice.update()
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            elif mydata.qt_type == 'coding':
                coding = model.Coding_model(**mydata)
                coding.question_qt_id = qt.qt_id
                coding.update()

                exam_question = model.Exam_question_model()
                exam_question.information_in_id = 1
                exam_question.qt_id = qt.qt_id
                exam_question.eq_lang = mydata.eq_lang
                exam_question.eq_qt_type = 'coding'
                exam_question.eq_pre_score = 100
                exam_question.eq_get_score = '-2'
                exam_question.eq_answer = coding.co_test_coding
                result = exam_question.insertBackid()
                eq_id = result[0]['max(eq_id)']
                for i in range(60):
                    time.sleep(1)
                    exam_question = model.Exam_question_model.getByPK(eq_id)
                    if exam_question.eq_get_score == 100:
                        response = util.Response(status=util.Status.__success__)
                        return util.objtojson(response)
                    if exam_question.eq_get_score == 0 or i == 59:
                        recover_coding.update()
                        recover_question.update()
                        qt.update()
                        response = util.Response(status=util.Status.__error__)
                        return util.objtojson(response)
            elif mydata.qt_type == 'filla':
                Filla = model.Filla_model(**mydata)
                Filla.question_qt_id = qt.qt_id
                Filla.update()
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            elif mydata.qt_type == 'fillb':
                Fillb = model.Fillb_model(**mydata)
                Fillb.question_qt_id = qt.qt_id
                Fillb.update()
                exam_question = model.Exam_question_model()
                exam_question.information_in_id = 1
                exam_question.qt_id = qt.qt_id
                exam_question.eq_qt_type = 'fillb'
                exam_question.eq_pre_score = 100
                exam_question.eq_get_score = '-2'
                exam_question.eq_answer = Fillb.fb_pre_coding
                exam_question.fillb_coding = Fillb.fb_pre_coding.replace('&&&', ' ')
                result = exam_question.insertBackid()
                eq_id = result[0]['max(eq_id)']
                for i in range(60):
                    time.sleep(1)
                    exam_question = model.Exam_question_model.getByPK(eq_id)
                    if exam_question.eq_get_score == 100:
                        response = util.Response(status=util.Status.__success__)
                        return util.objtojson(response)
                    if exam_question.eq_get_score == 0 or i == 59:
                        recover_fillb.update()
                        recover_question.update()
                        qt.update()
                        response = util.Response(status=util.Status.__error__)
                        return util.objtojson(response)
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            elif mydata.qt_type == 'judge':
                Judge = model.Judge_model(**mydata)
                Judge.question_qt_id = qt.qt_id
                Judge.update()
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)          


# 查找题目
class SelectQuestion:
    def POST(self):
        mydata = web.input()
        qbhq = model.Questions_bank_has_question_model()
        web.header("Access-Control-Allow-Origin", "*")
        question = model.Question_model()
        Knowledge = model.Knowledge_model()       
        must_params = set({'qb_id','qt_type','qt_diffculty_up','qt_diffculty_down','knowledge_kl_id'})
        mydata.qt_diffculty_down = int(mydata.qt_diffculty_down)
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            # 通过题库ID获取该题库下所有题目ID          
            question_id = qbhq.getByArgs(questions_bank_qb_id = mydata.qb_id)
            # print question_id
            question_list = []
            count = 0
            for k in question_id:         
                if mydata.knowledge_kl_id == 'all' and mydata.qt_type == 'all':
                    result = question.query('select * from question where qt_id = %s and qt_diffculty between %s and %s '%(k.question_qt_id,mydata.qt_diffculty_down+5,mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result ]
                    if result1:
                        qt=result1[0]
                        qt['qt_type']=util.type[qt.qt_type]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name 
                        question_list.append(qt)
                        count+=1
                elif mydata.qt_type == 'all':
                    result = question.query('select * from question where qt_id = %s and knowledge_kl_id = %s and qt_diffculty between %s and %s '%(k.question_qt_id,mydata.knowledge_kl_id,mydata.qt_diffculty_down+5,mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result ]
                    if result1:
                        qt=result1[0]
                        qt['qt_type']=util.type[qt.qt_type]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name 
                        question_list.append(qt)
                        count+=1
                    else:
                        print('空')
                elif mydata.knowledge_kl_id == 'all':
                    result = question.query('select * from question where qt_id = %s and qt_type = %s and qt_diffculty between %s and %s '%(k.question_qt_id,mydata.qt_type,mydata.qt_diffculty_down+5,mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result ]
                    if result1:
                        qt=result1[0]
                        qt['qt_type']=util.type[qt.qt_type]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name 
                        question_list.append(qt)
                        count+=1
                    else:
                        print('空')
                        # KnowledgeData = Knowledge.getByArgs(kl_id = result1[0].knowledge_kl_id)
                else:
                    result = question.query('select * from question where qt_id = %s and qt_type = %s and knowledge_kl_id = %s and qt_diffculty between %s and %s '%(k.question_qt_id,mydata.qt_type,mydata.knowledge_kl_id,mydata.qt_diffculty_down+5,mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result ]
                    if result1:
                        qt=result1[0]
                        qt['qt_type']=util.type[qt.qt_type]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name 
                        question_list.append(qt)
                        count+=1
                    else:
                        print('空')
            currentPage = int(mydata.currentPage)-1
            print(count)
            if (currentPage*10+10 < count):
                questiondata=question_list[currentPage*10:currentPage*10+10]
            else:
                questiondata=question_list[currentPage*10:count]
            page = util.Page(data = questiondata, totalRow = count, currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = "未知")
            response = util.Response(status = util.Status.__success__,body = page)
            return util.objtojson(response)


# 导出题目
class QuestionPrint:
    def POST(self):
        mydata = web.input()
        qbhq = model.Questions_bank_has_question_model()
        web.header("Access-Control-Allow-Origin", "*")
        question = model.Question_model()
        Knowledge = model.Knowledge_model()
        must_params = set({'qb_id', 'qt_type', 'qt_diffculty_up', 'qt_diffculty_down', 'knowledge_kl_id'})
        mydata.qt_diffculty_down = int(mydata.qt_diffculty_down)
        if (util.paramsok(must_params, mydata) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            # 通过题库ID获取该题库下所有题目ID
            question_id = qbhq.getByArgs(questions_bank_qb_id=mydata.qb_id)
            # print question_id
            question_list = []
            count = 0
            for k in question_id:
                if mydata.knowledge_kl_id == 'all' and mydata.qt_type == 'all':
                    result = question.query(
                        'select * from question where qt_id = %s and qt_diffculty between %s and %s ' % (
                            k.question_qt_id, mydata.qt_diffculty_down + 5, mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result]
                    if result1:
                        qt = result1[0]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name
                        question_list.append(qt)
                        count += 1
                elif mydata.qt_type == 'all':
                    result = question.query(
                        'select * from question where qt_id = %s and knowledge_kl_id = %s and qt_diffculty between %s and %s ' % (
                            k.question_qt_id, mydata.knowledge_kl_id, mydata.qt_diffculty_down + 5,
                            mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result]
                    if result1:
                        qt = result1[0]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name
                        question_list.append(qt)
                        count += 1
                    else:
                        print('空')
                elif mydata.knowledge_kl_id == 'all':
                    result = question.query(
                        'select * from question where qt_id = %s and qt_type = %s and qt_diffculty between %s and %s ' % (
                            k.question_qt_id, mydata.qt_type, mydata.qt_diffculty_down + 5, mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result]
                    if result1:
                        qt = result1[0]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name
                        question_list.append(qt)
                        count += 1
                    else:
                        print('空')
                        # KnowledgeData = Knowledge.getByArgs(kl_id = result1[0].knowledge_kl_id)
                else:
                    result = question.query(
                        'select * from question where qt_id = %s and qt_type = %s and knowledge_kl_id = %s and qt_diffculty between %s and %s ' % (
                            k.question_qt_id, mydata.qt_type, mydata.knowledge_kl_id, mydata.qt_diffculty_down + 5,
                            mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result]
                    if result1:
                        qt = result1[0]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name
                        question_list.append(qt)
                        count += 1
                    else:
                        print('空')
            now = datetime.datetime.now()
            question_bank = model.Questions_bank_model.getByPK(mydata.qb_id)
            filepath = str(
                u'%s/%s.docx' % (exampage_source, question_bank.qb_name))
            util.QuestionWord(question_list,mydata.qb_id,filepath)
            # currentPage = int(mydata.currentPage) - 1
            # print count
            # if (currentPage * 10 + 10 < count):
            #     questiondata = question_list[currentPage * 10:currentPage * 10 + 10]
            # else:
            #     questiondata = question_list[currentPage * 10:count]
            # page = util.Page(data=questiondata, totalRow=count, currentPage=int(mydata.currentPage),
            #                  pageSize=10, status=util.Status.__success__, message="未知")
            response = util.Response(status=util.Status.__success__,message=u'/source/exampage/%s.docx'%(question_bank.qb_name))
            return util.objtojson(response)


# 模糊查找
class FuzzySearch:
    def POST(self):
        mydata = web.input()
        print("查找题目，模糊查找", mydata)
        web.header("Access-Control-Allow-Origin", "*")
        must_params = set({'qt_stem','currentPage',})
        question = model.Question_model()
        Knowledge = model.Knowledge_model() 
        currentPage = int(mydata.currentPage)-1;
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            result = orm.db.query('select * from question where qt_stem like \'%%%s%%\'\
                order by qt_id limit %s,%s'%(mydata.qt_stem,currentPage*10,10))
            # result = orm.db.query('select * from question where qt_stem like \'%%%s%%\''%(mydata.qt_stem))
            questionlist = []
            result = [model.Question_model(**item) for item in result ]
            print(result)
            result1= question.query('select count(*) from question where qt_stem like \'%%%s%%\''%(mydata.qt_stem))
            count = result1[0]['count(*)']
            for params in result:
                qt = params
                qt['qt_type']=util.type[qt.qt_type]
                Knowledge = model.Knowledge_model()
                KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id) 
                qt['kl_name'] = KnowledgeData.kl_name 
                questionlist.append(qt)
            # response = util.Response(status=util.Status.__success__,body = questionlist)
            # return util.objtojson(response)
            page = util.Page(data = questionlist, totalRow = count, currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = "未知")
            response = util.Response(status=util.Status.__success__,body=page)
            print(util.objtojson(response))
            return util.objtojson(response)


# 删除题目
class DeleteQuestion:
    def POST(self):
        mydata = web.input()
        print("删除题目", mydata)
        qbhq = model.Questions_bank_has_question_model()
        web.header("Access-Control-Allow-Origin", "*")
        must_params = set({'qt_id'})
        #util.getFileRotatingLog().debug(mydata)
        session = web.ctx.session
        teacher = model.Teacher_model.getByArgs(tc_level='管理员')
        try:
            if(util.paramsok(must_params,mydata) == 2):
                response = util.Response(status = util.Status.__params_not_ok__)
                return util.objtojson(response)
            elif mydata.qb_id == "all":

                if str(mydata.deletepassword) == teacher[0].tc_password:
                    result = qbhq.getByArgs(question_qt_id = mydata.qt_id)
                    for k in result:
                        qbhq.qbhq_id = k.qbhq_id
                        qbhq.delete()
                    response = util.Response(status = util.Status.__success__)
                    return util.objtojson(response)
                else:
                    response = util.Response(status=util.Status.__error__,message="密码错误")
                    return util.objtojson(response)
            else:
                if str(mydata.deletepassword) == teacher[0].tc_password:
                    result = qbhq.query('select * from questions_bank_has_question where question_qt_id = %s \
                                 and questions_bank_qb_id = %s'%(mydata.qt_id,mydata.qb_id))
                    qbhq = model.Questions_bank_has_question_model(**result[0])
                    qbhq.delete()
                    response = util.Response(status=util.Status.__success__)
                    return util.objtojson(response)
                else:
                    response = util.Response(status=util.Status.__error__,message="密码错误")
                    return util.objtojson(response)
        except Exception as e:
           util.getFileRotatingLog().debug(e)
           response = util.Response(status=util.Status.__error__,message="删除失败")
           return util.objtojson(response)


# 导入题目
class BatchAddQuestion:
    def POST(self):
        mydata = web.input()
        print("导入： 获取的前台数据：", mydata)
        web.header("Access-Control-Allow-Origin", "*")
        must_params = set({'question_qt_id','questions_bank_qb_id'})
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            data = mydata.question_qt_id
            # 从1开始,最后一个无效
            question_qt_id = data.split(',')
            print(question_qt_id)
            qbhq = model.Questions_bank_has_question_model()
            for k in range(1,len(question_qt_id)-1):
                qbhq.question_qt_id = question_qt_id[k]
                qbhq.questions_bank_qb_id = mydata.questions_bank_qb_id
                qbhq.insert()
            response = util.Response(status = util.Status.__success__,)
            print("导入： 后台的返回数据：", util.objtojson(response))
            return util.objtojson(response)


# 导入题目,过滤重复题目
class FiltrationQuestion:
    def POST(self):
        mydata = web.input()
        print("接收的前台数据：", mydata)
        print(111111111111111111111)
        qbhq = model.Questions_bank_has_question_model()
        web.header("Access-Control-Allow-Origin", "*")
        question = model.Question_model()
        Knowledge = model.Knowledge_model()
        must_params = set({'qb_id','qt_type','qt_diffculty_up','qt_diffculty_down','knowledge_kl_id'})
        mydata.qt_diffculty_down = int(mydata.qt_diffculty_down)
        questionbank1 = model.Questions_bank_model()
        questionbank2 = model.Questions_bank_model()
        questionbank1 = questionbank1.getByArgs(qb_id = mydata.qb_id)
        questionbank2 = questionbank2.getByArgs(qb_id = mydata.questions_bank_qb_id)
        print(questionbank1)
        print(questionbank2)
        if questionbank1[0]['qb_lang'] != questionbank2[0]['qb_lang']:
            response = util.Response(status=util.Status.__error__, message="语言不一致,导题失败!")
            print(util.objtojson(response))
            return util.objtojson(response)
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            # 通过题库ID获取该题库下所有题目ID,并且不在导入题库里
            question_id = qbhq.getByArgs(questions_bank_qb_id = mydata.qb_id)
            question_id = qbhq.query('select * from questions_bank_has_question where \
                  questions_bank_qb_id = %s and question_qt_id not in (select \
                   question_qt_id from questions_bank_has_question where  \
                   questions_bank_qb_id = %s)'%(mydata.qb_id,mydata.questions_bank_qb_id))
            question_id = [model.Questions_bank_has_question_model(**item) for item in question_id]
            # print question_id
            question_list = []
            count = 0
            for k in question_id:
                if mydata.knowledge_kl_id == 'all' and mydata.qt_type == 'all':
                    result = question.query('select * from question where qt_id = %s and qt_diffculty between %s and %s '%(k.question_qt_id,mydata.qt_diffculty_down+5,mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result ]
                    if result1:
                        qt=result1[0]
                        qt['qt_type']=util.type[qt.qt_type]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name
                        question_list.append(qt)
                        count+=1
                elif mydata.qt_type == 'all':
                    result = question.query('select * from question where qt_id = %s and knowledge_kl_id = %s and qt_diffculty between %s and %s '%(k.question_qt_id,mydata.knowledge_kl_id,mydata.qt_diffculty_down+5,mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result ]
                    if result1:
                        qt=result1[0]
                        qt['qt_type']=util.type[qt.qt_type]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name
                        question_list.append(qt)
                        count+=1
                    else:
                        print('空')
                elif mydata.knowledge_kl_id == 'all':
                    result = question.query('select * from question where qt_id = %s and qt_type = %s and qt_diffculty between %s and %s '%(k.question_qt_id,mydata.qt_type,mydata.qt_diffculty_down+5,mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result ]
                    if result1:
                        qt=result1[0]
                        qt['qt_type']=util.type[qt.qt_type]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name
                        question_list.append(qt)
                        count+=1
                    else:
                        print('空')
                        # KnowledgeData = Knowledge.getByArgs(kl_id = result1[0].knowledge_kl_id)
                else:
                    result = question.query('select * from question where qt_id = %s and qt_type = %s and knowledge_kl_id = %s and qt_diffculty between %s and %s '%(k.question_qt_id,mydata.qt_type,mydata.knowledge_kl_id,mydata.qt_diffculty_down+5,mydata.qt_diffculty_up))
                    result1 = [model.Question_model(**item) for item in result ]
                    if result1:
                        qt=result1[0]
                        qt['qt_type']=util.type[qt.qt_type]
                        KnowledgeData = Knowledge.getByPK(qt.knowledge_kl_id)
                        qt['kl_name'] = KnowledgeData.kl_name
                        question_list.append(qt)
                        count+=1
                    else:
                        print('空')
            currentPage = int(mydata.currentPage)-1
            print(count)
            if (currentPage*10+10 < count):
                questiondata=question_list[currentPage*10:currentPage*10+10]
            else:
                questiondata=question_list[currentPage*10:count]
            page = util.Page(data = questiondata, totalRow = count, currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = "未知")
            response = util.Response(status = util.Status.__success__,body = page)
            print("返回值： ", util.objtojson(response))
            return util.objtojson(response)


# 根据题库id获取题库语言
class Getlang:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        mydata = web.input()
        #mydata={'qb_id': 1081}
        print(mydata)
        qb = model.Questions_bank_model()
        response = qb.getByArgs(qb_id=mydata['qb_id'])
        print("返回值： ", util.objtojson(response))
        return util.objtojson(response)


app = web.application(urls,globals())
render = web.template.render('template')
if __name__ == '__main__':
    
    if len(urls)&1 == 1:
        print("urls error, the size of urls must be even.")
    else:
        app.run()

