#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import util
sys.path.append('../')
from config import configs
from model import model
from model import orm

import web
import xlwt
import StringIO
urls = (
    '/','index',
    'selectScore/','selectScore',
    'getdata/','getdata',
    'printToExcel/','printToExcel'
    
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


class selectScore:
    def POST(self):
        debug=0
        if debug == 1:
            class Mydata:
                pass
            mydata=Mydata()
            mydata.ex_id=4
            mydata.cl_id=2
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
            return util.objtojson(response)


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
        sio=StringIO.StringIO()
        wb.save(sio)   #这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
        return sio.getvalue()

app = web.application(urls,globals())
render = web.template.render('template')