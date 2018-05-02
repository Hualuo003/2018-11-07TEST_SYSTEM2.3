#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

import time

import thread

import datetime
import web

from model.model import Strategy_model
from model import model
from model import orm
import util
from model.orm import *

urls = (
    '/', 'index',
    '/CreatStrategyTerm', 'CreatStrategyTerm',
    '/ChangeStrategyTerm', 'ChangeStrategyTerm',
    '/DelStrategyTerm', 'DelStrategyTerm',
    '/SelectStrategyTerm', 'SelectStrategyTerm',
    '/CreatStrategy', 'CreatStrategy',
    '/ChangeStrategy', 'ChangeStrategy',
    '/DelStrategy', 'DelStrategy',
    '/SelectStrategyTerm', 'SelectStrategyTerm',
    '/SelectStrategy', 'SelectStrategy',
    '/AddExam', 'AddExam',
    '/SelectAllExam', 'SelectAllExam',
    '/ChangeExam', 'ChangeExam',
    '/DelExam', 'DelExam',
    '/SelectExamByStrategyId', 'SelectExamByStrategyId',
    '/SelectExamById', 'SelectExamById',
    '/LoginExam', 'LoginExam',
    '/StartExamByUser', 'StartExamByUser',
    '/StopExamByUser', 'StopExamByUser',
    '/GetStrategyTerm', 'GetStrategyTerm',
    '/GetStrategy', 'GetStrategy',
    '/SelectExamByExamId', 'SelectExamByExamId',
    '/SelectExamByName', 'SelectExamByName',
    '/SelectExamQuestionById', 'SelectExamQuestionById',
    '/GetAllExam', 'GetAllExam',
    '/GetExamByEx_state', 'GetExamByEx_state',
)

app = web.application(urls, globals())
render = web.template.render('templates/')


class index:
    def GET(self):
        return render.index()


# 添加策略项
class CreatStrategyTerm:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        strategyTerm = model.Strategy_term_model()
        must_params = strategyTerm.__notnull__
        if (util.paramsok(must_params, params) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            strategyTerm = model.Strategy_term_model(**params)
            sm_type = "'" + strategyTerm.sm_type + "'"
            # 判断题库题目数量是否足够,知识点id未0表示所有知识点
            if strategyTerm.sm_knowledge == "0":
                # str = 'select count(*) from question where qt_id in \
                #         (select question_qt_id from questions_bank_has_question where \
                #         questions_bank_qb_id = %s) and qt_type=%s and \
                #         qt_diffculty > %s and qt_diffculty <= %s' % (strategyTerm.qb_id, sm_type,\
                #         int(strategyTerm.sm_difficulty_low),int(strategyTerm.sm_difficulty_high))

                question_result = strategyTerm.query('select count(*) from question where qt_id in \
                        (select question_qt_id from questions_bank_has_question where \
                        questions_bank_qb_id = %s) and qt_type=%s and \
                        qt_diffculty > %s and qt_diffculty <= %s' % (strategyTerm.qb_id, sm_type, \
                                                                     int(strategyTerm.sm_difficulty_low),
                                                                     int(strategyTerm.sm_difficulty_high)))
                count = int(question_result[0]['count(*)'])
            else:
                question_result = strategyTerm.query('select count(*) from question where qt_id in \
                    (select question_qt_id from questions_bank_has_question where \
                    questions_bank_qb_id = %s) and qt_type=%s and knowledge_kl_id =%s \
                    and qt_diffculty > %s and qt_diffculty <= %s' % (strategyTerm.qb_id, sm_type, \
                                                                     strategyTerm.sm_knowledge,
                                                                     int(strategyTerm.sm_difficulty_low),
                                                                     int(strategyTerm.sm_difficulty_high)))
                count = int(question_result[0]['count(*)'])
            if count < int(strategyTerm.sm_number):
                # result_message = "question num error "
                result_message = u"题库中没有足够的题符合策略项 "
                response = util.Response(status=util.Status.__error__, body=result_message, )
                return util.objtojson(response)
            # 判断是否与策略项有交集
            if strategyTerm.sm_knowledge == "0":
                result = strategyTerm.query('select * from strategy_term where strategy_sg_id =%s and sm_type = %s' \
                                            % (strategyTerm.strategy_sg_id, sm_type,))
                result = [model.Strategy_term_model(**item) for item in result]
            else:
                result = strategyTerm.query('select * from strategy_term where strategy_sg_id =%s and sm_type = %s and \
                            sm_knowledge = %s' % (strategyTerm.strategy_sg_id, sm_type, strategyTerm.sm_knowledge))
                result = [model.Strategy_term_model(**item) for item in result]

            for item in result:
                if int(item.sm_difficulty_low) < int(strategyTerm.sm_difficulty_low) and \
                        int(item.sm_difficulty_high) <= int(strategyTerm.sm_difficulty_low) \
                        or int(strategyTerm.sm_difficulty_low) < int(item.sm_difficulty_low) \
                        and int(strategyTerm.sm_difficulty_high) <= int(item.sm_difficulty_low):
                    print '无交集'
                else:
                    # result_message = "diffculty error"
                    result_message = u"难度交叉"
                    response = util.Response(status=util.Status.__error__, body=result_message)
                    return util.objtojson(response)
            if strategyTerm.insert():
                currentPage = int(params.currentPage) - 1
                result = strategyTerm.query(
                    'select * from strategy_term where strategy_sg_id =%s order by sm_id desc limit %s,%s' % \
                    (strategyTerm.strategy_sg_id, currentPage * 5, 5))
                strategyTermList = []
                total_score = 0
                for item in result:
                    item['sm_type'] = util.type[item.sm_type]
                    Knowledge = model.Knowledge_model()
                    if item.sm_knowledge == 0:
                        item['kl_name'] = "全部知识点"
                    else:
                        KnowledgeData = Knowledge.getByPK(item.sm_knowledge)
                        item['kl_name'] = KnowledgeData.kl_name
                    total_score += float(item['sm_score']) * float(item['sm_number'])
                    strategyTermList.append(item)
                strategy = model.Strategy_model()
                strategy.sg_id = strategyTerm.strategy_sg_id
                strategy.sg_score = total_score
                strategy.update()
                result = strategyTerm.query('select count(*) from strategy_term where strategy_sg_id =%s' % \
                                            (strategyTerm.strategy_sg_id))
                page = util.Page(data=strategyTermList, totalRow=int(result[0]['count(*)']) * 2,
                                 currentPage=int(params.currentPage), pageSize=5,
                                 status=util.Status.__success__, message=total_score)
                print page
                response = util.Response(status=util.Status.__success__, body=page)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)


# 获取策略项信息
class GetStrategyTerm:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        strategyTerm = model.Strategy_term_model(**params)
        currentPage = int(params.currentPage) - 1
        result = strategyTerm.query('select * from strategy_term where strategy_sg_id =%s \
            order by sm_id desc limit %s,%s' % (strategyTerm.strategy_sg_id, currentPage * 5, 5))
        strategyTermList = []
        total_score = 0
        for item in result:
            item['sm_type'] = util.type[item.sm_type]
            Knowledge = model.Knowledge_model()
            if item.sm_knowledge == 0:
                print "sou you"
                item['kl_name'] = "全部知识点"
            else:
                KnowledgeData = Knowledge.getByPK(item.sm_knowledge)
                item['kl_name'] = KnowledgeData.kl_name

            total_score += int(item['sm_score']) * int(item['sm_number'])
            strategyTermList.append(item)
        strategy = model.Strategy_model()
        strategy.sg_id = strategyTerm.strategy_sg_id
        strategy.sg_score = total_score
        strategy.update()
        result = strategyTerm.query('select count(*) from strategy_term where \
            strategy_sg_id =%s' % (strategyTerm.strategy_sg_id))
        page = util.Page(data=strategyTermList, totalRow=result[0]['count(*)'], currentPage=int(params.currentPage),
                         pageSize=5, status=util.Status.__success__, message=total_score)
        response = util.Response(status=util.Status.__success__, body=page)
        return util.objtojson(response)


# 修改策略项
class ChangeStrategyTerm:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        strategyTerm = model.Strategy_term_model()
        must_params = strategyTerm.__notnull__
        if (util.paramsok(must_params, params) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            strategyTerm = model.Strategy_term_model(**params)
            if strategyTerm.update():
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)


# 删除策略项
class DelStrategyTerm:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        strategyTerm = model.Strategy_term_model(**params)
        strategyTerm.delete()
        if strategyTerm.getByArgs(**params):
            response = util.Response(status=util.Status.__error__)
            return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__success__)
            return util.objtojson(response)


# 通过策略id查找策略项
# 参数

class SelectStrategyTerm:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        currentPage = params['requestPage'].encode('utf-8')
        print currentPage
        del params['requestPage']
        args = dict(strategy_sg_id=params.get('strategy_sg_id'))
        totalCount = model.Strategy_term_model.count(**args)
        lists = model.Strategy_term_model.getByPage(int(currentPage), **args)
        currentPage = int(currentPage) + 1
        page = util.Page(data=lists, totalRow=totalCount, currentPage=currentPage, pageSize=10,
                         status=util.Status.__success__, message="")
        return util.objtojson(page)


# 新建策略
class CreatStrategy:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        strategy = model.Strategy_model()
        must_params = strategy.__notnull__
        if (util.paramsok(must_params, params) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            strategy = model.Strategy_model(**params)
            if strategy.insert():
                result = strategy.getByArgs(sg_name=strategy.sg_name)
                response = util.Response(status=util.Status.__success__, body=result)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)


# 修改策略
class ChangeStrategy:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        strategy = model.Strategy_model()
        args = dict(sg_id=params.get('sg_id'))
        must_params = strategy.__notnull__
        if (util.paramsok(must_params, params) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            strategy = model.Strategy_model(**params)
            if strategy.getByArgs(**args):
                strategy.update()
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)


# 删除策略
class DelStrategy:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        strategy = model.Strategy_model(**params)
        strategy.delete()
        if Strategy_model.getByArgs(**params):
            response = util.Response(status=util.Status.__error__)
            return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__success__)
            return util.objtojson(response)


# 查询所有策略 分页查询
class SelectStrategy:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        mydata = web.input()
        count = model.Strategy_model.count();
        reasult = model.Strategy_model.getByPage(int(mydata.currentPage) - 1)
        page = util.Page(data=reasult, totalRow=count, currentPage=int(mydata.currentPage), pageSize=10,
                         status=util.Status.__success__, message="未知")
        response = util.Response(status=util.Status.__success__, body=page)
        return util.objtojson(response)
        # 查询所有策略 不分页查询


class GetStrategy:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        mydata = web.input()
        reasult = model.Strategy_model.getByArgs()
        response = util.Response(status=util.Status.__success__, body=reasult)
        return util.objtojson(response)

        # 添加考试


# class AddExam:
#     def POST(self):
#         web.header("Access-Control-Allow-Origin", "*")
#         params = web.input()
#         exam = model.Exam_model()
#         must_params = exam.__notnull__
#         if (util.paramsok(must_params, params) == 2):
#             response = util.Response(status=util.Status.__params_not_ok__)
#             return util.objtojson(response)
#         else:
#             exam = model.Exam_model(**params)
#             if exam.insert():
#                 # response = util.Response(status=util.Status.__success__)
#                 result = exam.query("select max(ex_id) from exam")
#                 lastExamId = int(result[0]['max(ex_id)'])
#                  # 获取教务班学生id
#                 stuHasClass = model.Student_has_class_model();
#                 classId = params['class_cl_id'].encode('utf-8')
#                 classId = classId.split(',')
#                 for k in range(1,len(classId)-1):
#                     listStuid = stuHasClass.getByArgs(class_cl_id = classId[k]);
#                     for stuID in listStuid:
#                         informationArgs = dict(student_st_id=stuID.student_st_id, exam_ex_id=lastExamId, class_cl_id = classId[k],sg_id=exam.strategy_sg_id)
#                         information = model.Information_model(**informationArgs)
#                         information.insert()
#                 return util.objtojson(response)
#             else:
#                 response = util.Response(status=util.Status.__error__)
#                 return util.objtojson(response)

# 添加考试
class AddExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        exam = model.Exam_model()
        must_params = exam.__notnull__
        if (util.paramsok(must_params, params) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            exam = model.Exam_model(**params)
            exam.ex_state = 0
            if exam.insert():
                result = exam.query("select max(ex_id) from exam")
                lastExamId = int(result[0]['max(ex_id)'])
                # 获取教务班学生id
                stuHasClass = model.Student_has_class_model();
                classId = params['class_cl_id'].encode('utf-8')
                classId = classId.split(',')
                for k in range(1, len(classId) - 1):
                    listStuid = stuHasClass.getByArgs(class_cl_id=classId[k]);
                    for stuID in listStuid:
                        informationArgs = dict(student_st_id=stuID.student_st_id, exam_ex_id=lastExamId,
                                               class_cl_id=classId[k], sg_id=exam.strategy_sg_id)
                        information = model.Information_model(**informationArgs)
                        information.insert()
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)


# 修改考试
class ChangeExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        exam = model.Exam_model()
        must_params = exam.__notnull__
        if (util.paramsok(must_params, params) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            exam = model.Exam_model(**params)
            exam.ex_state = 0
            if exam.update():
                # 获取教务班学生id
                stuHasClass = model.Student_has_class_model();
                classId = params['add_class_cl_id'].encode('utf-8')
                classId = classId.split(',')
                for k in range(1, len(classId) - 1):
                    listStuid = stuHasClass.getByArgs(class_cl_id=classId[k])
                    for stuID in listStuid:
                        informationArgs = dict(student_st_id=stuID.student_st_id, exam_ex_id=exam.ex_id,
                                               class_cl_id=classId[k], sg_id=exam.strategy_sg_id)
                        information = model.Information_model(**informationArgs)
                        information.insert()
                delete_classId = params['delete_class_cl_id'].encode('utf-8')
                delete_classId = delete_classId.split(',')
                for k in range(1, len(delete_classId) - 1):
                    listStuid = stuHasClass.getByArgs(class_cl_id=delete_classId[k])
                    for stuID in listStuid:
                        db.delete('information', where="student_st_id = $student_st_id \
                        and exam_ex_id = $exam_ex_id",
                                  vars={'student_st_id': stuID.student_st_id, 'exam_ex_id': exam.ex_id})

                #更新imformation策率子段
                db.update('information', where="exam_ex_id=%s" % (params.ex_id), sg_id=params.strategy_sg_id, )


                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)


# 分页查询考试
class SelectAllExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        count = model.Exam_model.count()
        currentPage = int(params.currentPage) - 1
        lists = model.Exam_model.query(
            'select * from exam order by ex_time_start desc limit %s,%s' % (currentPage * 10, 10))
        lists = [model.Exam_model(**item) for item in lists]
        for list in lists:
            start_time = list['ex_time_start'].strftime('%Y-%m-%d %H:%M:%S')
            end_time = list['ex_time_end'].strftime('%Y-%m-%d %H:%M:%S')
            del list['ex_time_start']
            del list['ex_time_end']
            list.setdefault('ex_time_start', start_time)
            list.setdefault('ex_time_end', end_time)
        page = util.Page(data=lists, totalRow=count, currentPage=int(params.currentPage), pageSize=10,
                         status=util.Status.__success__, message="未知")
        response = util.Response(status=util.Status.__success__, body=page)
        return util.objtojson(response)
        # 获取所有考试


class GetAllExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        lists = model.Exam_model.query('select * from exam order by ex_time_start desc')
        lists = [model.Exam_model(**item) for item in lists]
        for list in lists:
            start_time = list['ex_time_start'].strftime('%Y-%m-%d %H:%M:%S')
            end_time = list['ex_time_end'].strftime('%Y-%m-%d %H:%M:%S')
            del list['ex_time_start']
            del list['ex_time_end']
            list.setdefault('ex_time_start', start_time)
            list.setdefault('ex_time_end', end_time)
        response = util.Response(status=util.Status.__success__, body=lists)
        return util.objtojson(response)


class GetExamByEx_state:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        lists = model.Exam_model.query('select * from exam where ex_state = 1')
        lists = [model.Exam_model(**item) for item in lists]
        response = util.Response(status=util.Status.__success__, body=lists)
        return util.objtojson(response)


# 通过exam_id查找考试
class SelectExamByExamId:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        exam = model.Exam_model()
        data = exam.getByPK(int(params.ex_id))
        start_time = data['ex_time_start'].strftime('%Y-%m-%dT%H:%M')
        end_time = data['ex_time_end'].strftime('%Y-%m-%dT%H:%M')
        del data['ex_time_start']
        del data['ex_time_end']
        data.setdefault('ex_time_start', start_time)
        data.setdefault('ex_time_end', end_time)
        response = util.Response(status=util.Status.__success__, body=data)
        return util.objtojson(response)


# 通过名字，开始日期，结束日期查询考试
class SelectExamByName:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        currentPage = int(params.currentPage) - 1
        print params
        if params.ex_name == '':
            if params.ex_time_end == '' and params.ex_time_start != '':
                params.ex_time_end = '2200-12-12T12:12'
            if params.ex_time_end != '' and params.ex_time_start == '':
                params.ex_time_start = '2000-12-12T12:12'
            if params.ex_time_end == '' and params.ex_time_start == '':
                params.ex_time_start = '2000-12-12T12:12'
                params.ex_time_end = '2200-12-12T12:12'
            lists = model.Exam_model.query('select * from exam where ex_time_start >= %s \
                and ex_time_end <= %s order by ex_time_start desc limit %s,%s' \
                                           % ("'" + params.ex_time_start + "'", "'" + params.ex_time_end + "'",
                                              currentPage * 10, 10))
            result = model.Exam_model.query('select count(*) from exam where ex_time_start \
              >= %s and ex_time_end <= %s' % ("'" + params.ex_time_start + "'", "'" + params.ex_time_end + "'",))
        elif params.ex_time_start == '':
            lists = model.Exam_model.query('select * from exam where ex_name like \
              \'%%%s%%\' order by ex_time_start desc limit %s,%s' % (params.ex_name, currentPage * 10, 10))
            result = model.Exam_model.query('select count(*) from exam where ex_name like \
              \'%%%s%%\' ' % (params.ex_name))
        else:
            if params.ex_time_end == '':
                params.ex_time_end = '2200-12-12T12:12'
            lists = model.Exam_model.query('select * from exam where ex_name like \
              \'%%%s%%\' and ex_time_start >= %s and ex_time_end <= %s order by \
              ex_time_start desc limit %s,%s' % (
            params.ex_name, "'" + params.ex_time_start + "'", "'" + params.ex_time_end + "'", \
            currentPage * 10, 10))
            result = model.Exam_model.query('select count(*) from exam where ex_name like \
              \'%%%s%%\' and ex_time_start >= %s and ex_time_end <= %s' \
                                            % (params.ex_name, "'" + params.ex_time_start + "'",
                                               "'" + params.ex_time_end + "'",))
        count = result[0]['count(*)']
        lists = [model.Exam_model(**item) for item in lists]
        print lists
        for list in lists:
            start_time = list['ex_time_start'].strftime('%Y-%m-%d %H:%M:%S')
            end_time = list['ex_time_end'].strftime('%Y-%m-%d %H:%M:%S')
            del list['ex_time_start']
            del list['ex_time_end']
            list.setdefault('ex_time_start', start_time)
            list.setdefault('ex_time_end', end_time)
        page = util.Page(data=lists, totalRow=count, currentPage=int(params.currentPage), pageSize=10,
                         status=util.Status.__success__, message="未知")
        response = util.Response(status=util.Status.__success__, body=page)
        return util.objtojson(response)

        # 通过策略id查找考试


class SelectExamByStrategyId:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        exam = model.Exam_model()
        data = exam.getByArgs(**params)
        start_time = data[0]['ex_time_start'].strftime('%Y-%m-%d %H:%M:%S')
        end_time = data[0]['ex_time_end'].strftime('%Y-%m-%d %H:%M:%S')
        del data[0]['ex_time_start']
        del data[0]['ex_time_end']
        data[0].setdefault('ex_time_start', start_time)
        data[0].setdefault('ex_time_end', end_time)
        return util.objtojson(data)


# 删除考试
class DelExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        exam = model.Exam_model(**params)
        exam.delete()
        if exam.getByArgs(**params):
            response = util.Response(status=util.Status.__error__)
            return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__success__)
            return util.objtojson(response)


# 根据考试id查询考试题目
# 参数：ex_id
class SelectExamQuestionById:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        information = model.Information_model()
        # 获取策略id
        if 1:
            # args = dict(exam_ex_id = params.ex_id,student_st_id=params.student_id)
            # information_data = information.getByArgs(**args)
            information_data = information.query('SELECT * FROM information WHERE \
                student_st_id=%s and exam_ex_id=%s' % (params.student_id, params.ex_id))
            information_data = [model.Information_model(**item) for item in information_data]

            # 获取策略项
            # 难度上下限、知识点、题型、数量、题库id-->题目id(多个要大于数量)
            lists = model.Strategy_term_model.getByArgs(strategy_sg_id=information_data[0]['sg_id'])
            # 选中的题目
            choice_question = []
            judge_question = []
            # filla是读程序写结果
            filla_question = []
            fillb_question = []
            coding_question = []
            for strategy_term in lists:
                if strategy_term.sm_type == 'choice':
                    result = model.Question_model.query('select * from question where qt_id \
                        in (select question_qt_id from questions_bank_has_question where \
                        questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                        = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'choice' + "'",
                                                         strategy_term.sm_knowledge, \
                                                         strategy_term.sm_difficulty_low + 5,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                    for question in result:
                        qt_id = question.qt_id
                        choice_data = model.Choice_model.getByPK(qt_id)
                        question['score'] = strategy_term.sm_score

                        # 添加exam_question
                        exam_question = model.Exam_question_model()
                        exam_question.information_in_id = information_data[0]['in_id']
                        exam_question['qt_id'] = qt_id
                        exam_question.eq_qt_type = question.qt_type
                        exam_question.eq_pre_score = strategy_term.sm_score
                        eq_id = exam_question.insertBackid()

                        question['eq_id'] = eq_id[0]['max(eq_id)']
                        question = dict(question, **choice_data)
                        choice_question.append(question)

                if strategy_term.sm_type == 'judge':
                    result = model.Question_model.query('select * from question where qt_id \
                        in (select question_qt_id from questions_bank_has_question where \
                        questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                        = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'judge' + "'",
                                                         strategy_term.sm_knowledge, \
                                                         strategy_term.sm_difficulty_low + 5,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                    for question in result:
                        judge_data = model.Judge_model.getByPK(question.qt_id)
                        question['score'] = strategy_term.sm_score

                        # 添加exam_question
                        exam_question = model.Exam_question_model()
                        exam_question.information_in_id = information_data[0]['in_id']
                        exam_question.qt_id = question.qt_id
                        exam_question.eq_qt_type = question.qt_type
                        exam_question.eq_pre_score = strategy_term.sm_score
                        eq_id = exam_question.insertBackid()

                        question['eq_id'] = eq_id[0]['max(eq_id)']
                        question = dict(question, **judge_data)
                        judge_question.append(question)
                if strategy_term.sm_type == 'filla':
                    result = model.Question_model.query('select * from question where qt_id \
                        in (select question_qt_id from questions_bank_has_question where \
                        questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                        = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'filla' + "'",
                                                         strategy_term.sm_knowledge, \
                                                         strategy_term.sm_difficulty_low + 5,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                    for question in result:
                        filla_data = model.Filla_model.getByPK(question.qt_id)
                        question['score'] = strategy_term.sm_score

                        # 添加exam_question
                        exam_question = model.Exam_question_model()
                        exam_question.information_in_id = information_data[0]['in_id']
                        exam_question.qt_id = question.qt_id
                        exam_question.eq_qt_type = question.qt_type
                        exam_question.eq_pre_score = strategy_term.sm_score
                        eq_id = exam_question.insertBackid()

                        question['eq_id'] = eq_id[0]['max(eq_id)']
                        question = dict(question, **filla_data)
                        filla_question.append(question)
                if strategy_term.sm_type == 'fillb':
                    result = model.Question_model.query('select * from question where qt_id \
                        in (select question_qt_id from questions_bank_has_question where \
                        questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                        = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'fillb' + "'",
                                                         strategy_term.sm_knowledge, \
                                                         strategy_term.sm_difficulty_low + 5,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                    for question in result:
                        fillb_data = model.Fillb_model.getByPK(question.qt_id)
                        question['score'] = strategy_term.sm_score
                        # 统计空数量
                        count = fillb_data.fb_pre_coding.count("&&&")
                        count = count / 2

                        eq_id_data = []
                        while count > 0:
                            count = count - 1;
                            # 添加exam_question
                            exam_question = model.Exam_question_model()
                            exam_question.information_in_id = information_data[0]['in_id']
                            exam_question.qt_id = question.qt_id
                            exam_question.eq_qt_type = question.qt_type
                            exam_question.eq_pre_score = strategy_term.sm_score
                            eq_id = exam_question.insertBackid()
                            eq_id_data.append(eq_id[0]['max(eq_id)'])
                            pass
                        question = dict(question, **fillb_data)
                        fillb_data = []
                        fillb_data.append(question)
                        fillb_data.append(eq_id_data)
                        fillb_question.append(fillb_data)
                if strategy_term.sm_type == 'coding':
                    result = model.Question_model.query('select * from question where qt_id \
                        in (select question_qt_id from questions_bank_has_question where \
                        questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                        = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'coding' + "'",
                                                         strategy_term.sm_knowledge, \
                                                         strategy_term.sm_difficulty_low + 5,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                    for question in result:
                        coding_data = model.Coding_model.getByPK(question.qt_id)
                        question['score'] = strategy_term.sm_score

                        # 添加exam_question
                        exam_question = model.Exam_question_model()
                        exam_question.information_in_id = information_data[0]['in_id']
                        exam_question.qt_id = question.qt_id
                        exam_question.eq_qt_type = question.qt_type
                        exam_question.eq_pre_score = strategy_term.sm_score
                        eq_id = exam_question.insertBackid()

                        question['eq_id'] = eq_id[0]['max(eq_id)']
                        question = dict(question, **coding_data)
                        coding_question.append(question)
            question_list = []
            question_list.append(choice_question)
            question_list.append(judge_question)
            question_list.append(filla_question)
            question_list.append(fillb_question)
            question_list.append(coding_question)
            response = util.Response(status=util.Status.__success__, body=question_list)
            print question_list
            print fillb_question
            return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__error__)
            return util.objtojson(response)


# class SelectExamQuestionById:
#     def POST(self):
#         web.header("Access-Control-Allow-Origin", "*")
#         params = web.input()
#         pk = params['ex_id']
#         exam = model.Exam_model()
#         # 获取策略id
#         if exam.getByPK(pk):
#             list = exam.getByPK(pk)
#             args = dict(strategy_sg_id=list.get('strategy_sg_id'))
#             # 获取策略项
#             # 难度上下限、知识点、题型、数量、题库id-->题目id(多个要大于数量)
#             lists = model.Strategy_term_model.getByArgs(**args)
#             # 选中的题目
#             choice_question = []
#             judge_question = []
#             # filla是读程序写结果
#             filla_question = []
#             fillb_question = []
#             coding_question = []
#             for strategy_term in lists:
#                 if strategy_term.sm_type=='choice':
#                     result = model.Question_model.query('select * from question where qt_id \
#                         in (select question_qt_id from questions_bank_has_question where \
#                         questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
#                         = %s and qt_diffculty between %s and %s order by rand() limit %s'%\
#                         (strategy_term.qb_id,"'"+'choice'+"'",strategy_term.sm_knowledge,\
#                         strategy_term.sm_difficulty_low,strategy_term.sm_difficulty_high,strategy_term.sm_number))
#                     result = [model.Question_model(**item) for item in result]
#                     for question in result:
#                         choice_data=model.Choice_model.getByPK(question.qt_id)
#                         question['score'] = strategy_term.sm_score
#                         question=dict(question, **choice_data)

#                         choice_question.append(question)

#                 if strategy_term.sm_type=='judge':
#                     result = model.Question_model.query('select * from question where qt_id \
#                         in (select question_qt_id from questions_bank_has_question where \
#                         questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
#                         = %s and qt_diffculty between %s and %s order by rand() limit %s'%\
#                         (strategy_term.qb_id,"'"+'judge'+"'",strategy_term.sm_knowledge,\
#                         strategy_term.sm_difficulty_low,strategy_term.sm_difficulty_high,strategy_term.sm_number))
#                     result = [model.Question_model(**item) for item in result]
#                     for question in result:
#                         judge_data=model.Judge_model.getByPK(question.qt_id)
#                         question['score'] = strategy_term.sm_score
#                         question=dict(question, **judge_data)
#                         judge_question.append(question)
#                 if strategy_term.sm_type=='filla':
#                     result = model.Question_model.query('select * from question where qt_id \
#                         in (select question_qt_id from questions_bank_has_question where \
#                         questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
#                         = %s and qt_diffculty between %s and %s order by rand() limit %s'%\
#                         (strategy_term.qb_id,"'"+'filla'+"'",strategy_term.sm_knowledge,\
#                         strategy_term.sm_difficulty_low,strategy_term.sm_difficulty_high,strategy_term.sm_number))
#                     result = [model.Question_model(**item) for item in result]
#                     for question in result:
#                         filla_data=model.Filla_model.getByPK(question.qt_id)
#                         question['score'] = strategy_term.sm_score
#                         question=dict(question, **filla_data)
#                         filla_question.append(question)
#                 if strategy_term.sm_type=='fillb':
#                     result = model.Question_model.query('select * from question where qt_id \
#                         in (select question_qt_id from questions_bank_has_question where \
#                         questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
#                         = %s and qt_diffculty between %s and %s order by rand() limit %s'%\
#                         (strategy_term.qb_id,"'"+'fillb'+"'",strategy_term.sm_knowledge,\
#                         strategy_term.sm_difficulty_low,strategy_term.sm_difficulty_high,strategy_term.sm_number))
#                     result = [model.Question_model(**item) for item in result]
#                     for question in result:
#                         fillb_data=model.Fillb_model.getByPK(question.qt_id)
#                         question['score'] = strategy_term.sm_score
#                         question=dict(question, **fillb_data)
#                         fillb_question.append(question)
#                 if strategy_term.sm_type=='coding':
#                     result = model.Question_model.query('select * from question where qt_id \
#                         in (select question_qt_id from questions_bank_has_question where \
#                         questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
#                         = %s and qt_diffculty between %s and %s order by rand() limit %s'%\
#                         (strategy_term.qb_id,"'"+'coding'+"'",strategy_term.sm_knowledge,\
#                         strategy_term.sm_difficulty_low,strategy_term.sm_difficulty_high,strategy_term.sm_number))
#                     result = [model.Question_model(**item) for item in result]
#                     for question in result:
#                         coding_data=model.Coding_model.getByPK(question.qt_id)
#                         question['score'] = strategy_term.sm_score
#                         question=dict(question, **coding_data)
#                         coding_question.append(question)
#             question_list = []
#             question_list.append(choice_question)
#             question_list.append(judge_question)
#             question_list.append(filla_question)
#             question_list.append(fillb_question)
#             question_list.append(coding_question)
#             response = util.Response(status=util.Status.__success__,body=question_list)
#             print question_list
#             return util.objtojson(response)
#         else:
#             response = util.Response(status=util.Status.__error__)
#             return util.objtojson(response)


# 学生登录考试
class LoginExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        params.setdefault("in_state", '1')
        params.setdefault("in_ip", web.ctx.ip)
        information = model.Information_model(**params)
        if information.update():
            response = util.Response(status=util.Status.__error__)
            return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__success__)
            return util.objtojson(response)


# 开始考试
class StartExamByUser:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        examId = params['ex_id']
        examStatus = dict(ex_state=1, ex_id=examId)
        exam = model.Exam_model(**examStatus)
        exam.update()


# 结束考试
class StopExamByUser:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        examId = params['ex_id']
        examStatus = dict(ex_state=2, ex_id=examId)
        exam = model.Exam_model(**examStatus)
        exam.update()


def upExamStatusStart(threadName, delay):
    while (1):
        print threadName
        time.sleep(delay)
        startExam = dict(ex_state=0)
        examModel = model.Exam_model()
        # 未开始的考试
        exams = examModel.getByArgs(**startExam)
        for exam in exams:
            if exam['ex_time_start'] < datetime.datetime.now():
                exam['ex_state'] = '1'
                exam.update()


def upExamStatusStop(threadName, delay):
    while (1):
        print threadName
        time.sleep(delay)
        startExam = dict(ex_state=1)
        examModel = model.Exam_model()
        # 未开始的考试
        exams = examModel.getByArgs(**startExam)
        for exam in exams:
            if exam['ex_time_end'] < datetime.datetime.now():
                exam['ex_state'] = '2'
                exam.update()


if __name__ == '__main__':

    if len(urls) & 1 == 1:
        print "urls error, the size of urls must be even."
    else:
        try:
            thread.start_new(upExamStatusStart, ("thread-1", 2,))
            thread.start_new(upExamStatusStop, ("thread-2", 4,))
            thread.start_new(app.run())
        except:
            print "Error: unable to start thread"
