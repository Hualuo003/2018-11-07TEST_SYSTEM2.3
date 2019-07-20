#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import util
sys.path.append('../')
from config import configs
from model import model
from model import orm
from model.model import *
from model.orm import *
import json

import web
import xlwt
import io         # py2 为StringIO，py3为io
urls = (
    '/','index',
    'selectScore/','selectScore',
    'getdata/','getdata',
    'printToExcel/','printToExcel',
    'getclass/', 'getclass',
    'getExamWeight/', 'getExamWeight'
)
class index:
    def GET(self):
        mydata = web.input(name=None)
        return 'admin page'
    def POST(self):
        mydata = web.input(name=None)
        return 'admin page'

class getdata:
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        cl = model.Class_model()
        exam = model.Exam_model()
        cl_data = cl.getByArgs()
        exam_data = exam.getByArgs()
        data = []
        data.append(cl_data)
        data.append(exam_data)
        response = util.Response(status = util.Status.__success__,body = data)
        return util.objtojson(response)


###############
# 更新 2018-10-12 兰红林
###############
class getclass:
    def GET(self):
        print("getclass--------------")
        web.header("Access-Control-Allow-Origin", "*")
        class_info = Class_model.query('select * from class')
        class_info = [Class_model(**item) for item in class_info]
        response = util.Response(status=util.Status.__success__, body=class_info)
        print(util.objtojson(response))
        return util.objtojson(response)

    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        mydata = web.input()
        print('printexam--------------', mydata)
        exam_list = Exam_model.query('select * from exam where ex_id in (select  distinct exam_ex_id from \
                     information where class_cl_id = %s)'%(int(mydata.cl_id)))
        exam_list = [Exam_model(**item) for item in exam_list]
        response = util.Response(status=util.Status.__success__, body=exam_list)
        print(util.objtojson(response))
        return util.objtojson(response)


# 获取考试权重
class getExamWeight:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        mydata = web.input()
        print('获取到的考试权重信息：------------------------\n', mydata)
        exam_id = mydata.exam
        exam_id = exam_id.split(',')
        exam_weight = mydata.weight
        exam_weight = exam_weight.split(',')
        ex_id = []
        ex_weight = []
        for i in range((len(exam_id)-1)):
            if(i > 0 ):
                ex_id.append(int(exam_id[i]))
                ex_weight.append(float(exam_weight[i]))
        print(ex_id)
        print(ex_weight)
        # 查询班级的所有学生
        student_list = Student_model.query('select * from student where st_id in(select student_st_id from \
                                student_has_class where class_cl_id = %d)' % (int(mydata.cl_id)))
        student_list = [Student_model(**item) for item in student_list]
        print(util.objtojson(student_list))
        print('-------------------------------------------')
        # for student in student_list:
        #     print(student)
        # ex_id = json.loads(ex_id)               # 将json格式数据转换为数据类型
        #print(ex_id)
        # weight = json.loads(ex_weight)
        #print(weight)
        # print(len(ex_id))
        # print(ex_id[2])
        # print(len(weight))
        # print(weight[1])
        for i in range(len(ex_id)):
            ex_name = Exam_model.query( ('select ex_name from exam where ex_id = %d') % (int(ex_id[i])))
            # print('查找考试名称的结果：', util.objtojson(ex_name))
            exam_name = (ex_name[0].ex_name)
            str = 'exam%d' % i
            print('解析出来的考试名称：', exam_name)
            for j in student_list:
                data = j
                exam = {}
                try:
                    data = data['data']
                except:
                    data['data']=[]
                    data = data['data']
                # print(util.objtojson(j))
                try:
                    score = Information_model.query('select in_score from information where\
                        (exam_ex_id = %d && student_st_id = %d && class_cl_id = %d)' % (ex_id[i], j['st_id'],int(mydata.cl_id)) )
                    # print('查找分数的结果：', util.objtojson(score))
                    score = (float)(score[0].in_score)
                except:
                    score = 0.0
                print('解析出来的分数', score)
                exam['ex_name'] = exam_name
                exam['ex_score'] = score
                exam['ex_weight'] = ex_weight[i]
                exam['ex_id'] = ex_id[i]
                if i == 0:
                    j['total'] = (float)(score) * (ex_weight[i])
                else:
                    j['total'] = j['total'] + (float)(score) * ex_weight[i]
                data.append(exam)
        for student in student_list:
            print(student)
        response = util.Response(status=util.Status.__success__, body=student_list)
        print(util.objtojson(response))
        return util.objtojson(response)


class selectScore:
    def POST(self):
        debug=0
        if debug == 1:
            class Mydata:
                pass
            mydata=Mydata()
            mydata.ex_id = 4
            mydata.cl_id = 2
        else:
            web.header("Access-Control-Allow-Origin", "*")
            mydata = web.input()
        student = model.Student_model()
        information_data = orm.db.query('select * from information where exam_ex_id = %s and class_cl_id = %s'%(mydata.ex_id,mydata.cl_id))
        information_data = [model.Information_model(**item) for item in information_data]
        data = []
        for single_information in information_data:
            single_student_data = []
            single_student_data.append(student.getByPK(single_information.student_st_id))
            single_student_data.append(single_information)
            single_information['in_state'] = util.in_state[int(single_information.in_state)]
            if single_information['in_score'] == -1:
                single_information['in_score'] = u'未出分'
            result = model.Exam_question_model.getByArgs(information_in_id=single_information.in_id)
            result_mapping = {'choice':[],'judge':[],'filla':[],'fillb':[],'coding':[]}
            for question in result:
                if question.eq_qt_type == 'fillb':
                    if len(result_mapping["fillb"])== 0 or result_mapping["fillb"][-1].qt_id != question.qt_id:
                        if question.eq_get_score<0:
                            question.eq_get_score=u'未出分'
                        result_mapping["fillb"].append(question)
                    elif result_mapping["fillb"][-1].qt_id == question.qt_id:
                        if result_mapping["fillb"][-1].eq_get_score==u'未出分' or question.eq_get_score<0:
                            result_mapping["fillb"][-1].eq_get_score = u'未出分'
                        else:
                            result_mapping["fillb"][-1].eq_get_score += question.eq_get_score
                else:
                    if question.eq_get_score < 0:
                        question.eq_get_score = u'未出分'
                    result_mapping[str(question.eq_qt_type)].append(question)
            examquestion_data = []
            examquestion_data.extend(result_mapping['choice'])
            examquestion_data.extend(result_mapping['judge'])
            examquestion_data.extend(result_mapping['filla'])
            examquestion_data.extend(result_mapping["fillb"])
            examquestion_data.extend(result_mapping['coding'])
            single_student_data.append(examquestion_data)
            print(single_student_data)
            data.append(single_student_data)
        if debug!=1:
            page = util.Page(data = data, totalRow = len(data), currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = "未知")
            response = util.Response(status = util.Status.__success__,body = page)
            #return util.objtojson(response)
            ls = list()
            for i in range(len(response.body.data)):
                dic = dict()
                dic['st_id'] = response.body.data[i][0].st_id
                dic['st_name'] = response.body.data[i][0].st_name
                dic['in_state'] = response.body.data[i][1].in_state
                dic['in_ip'] = response.body.data[i][1].in_ip
                dic['in_score'] = response.body.data[i][1].in_score
                ls.append(dic)
            print("返回数据：", util.objtojson(ls))
            return util.objtojson(ls)


if __name__ == "__main__":
    selectScore().POST()

class printToExcel:
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        web.header('Content-type','application/vnd.ms-excel')  #指定返回的类型
        web.header('Transfer-Encoding','chunked')
        web.header('Content-Disposition','attachment;filename="export.xls"') #设定用户浏览器显示的保存文件名
        wb=xlwt.Workbook()
        wb.encoding='gbk'
        ws=wb.add_sheet('1')
        ws.write(0,1,'123')  #如果要写中文请使用UNICODE
        sio=io.StringIO()
        wb.save(sio)   #这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()

app = web.application(urls,globals())
render = web.template.render('template')
