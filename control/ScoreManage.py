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
        web.header("Access-Control-Allow-Origin", "*")
        mydata = web.input()
        cl = model.Class_model()
        exam = model.Exam_model()
        information = model.Information_model()
        student = model.Student_model()
        information_data = orm.db.query('select * from information where exam_ex_id = %s and class_cl_id = %s'%(mydata.ex_id,mydata.cl_id))
        # information_data = orm.db.query('select * from information where exam_ex_id = %s'%(mydata.ex_id))
        information_data = [model.Information_model(**item) for item in information_data]
        student_data = []
        examquestion_data = []
        for k in information_data:
            result = student.getByArgs(st_id = k.student_st_id)
            student_data.append(result)
            k['in_state'] = util.in_state[int(k.in_state)]
            if k['in_score'] == -1:
                k['in_score'] = u'未出分'
            result = model.Exam_question_model.getByArgs(information_in_id=k.in_id)
            for question in result:
                if question.eq_get_score <0:
                    question.eq_get_score = u'未出分'
            examquestion_data.append(result)
        data = []
        data.append(information_data)
        data.append(student_data)
        data.append(examquestion_data)
        page = util.Page(data = data, totalRow = len(student_data), currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = "未知")
        response = util.Response(status = util.Status.__success__,body = page)
        return util.objtojson(response)

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
if __name__ == '__main__':
    
    if len(urls)&1 == 1:
        print "urls error, the size of urls must be even."
    else:
        app.run()