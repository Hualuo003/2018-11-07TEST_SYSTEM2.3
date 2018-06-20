#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

reload(sys)
sys.path.append('../')
sys.setdefaultencoding( "utf-8" )
import web
from model.model import *
from util import Status, Response
import util
from model.orm import *
import xlrd
from model import orm
from model import model
from config_default import student_source
urls = (
    '^ConfirmAddStudent$','ConfirmAddStudent',
    '^BatchAddStudent$','BatchAddStudent',
    '^ManageClass$','ManageClass',
    '^QueryClass$','QueryClass',
    '^UpdateClass$','UpdateClass',
    '^AddClass$','AddClass',
    '^DeleteClass$','DeleteClass',
    '^OpenClass$','OpenClass',
    '^DeleteStudent','DeleteStudent',
    '^CheckStudent','CheckStudent',
    '^QueryStudent','QueryStudent',
    '^GetClassInfo$','GetClassInfo',
    '^GetClassByExam$','GetClassByExam',
    '^GetStudentByExam$','GetStudentByExam',
)
class GetClassInfo:
    def POST(self):
        web.header("Access-Control-Allow-Origin","*")
        class_info = Class_model.getByArgs()
        response =  util.Response(Status. __success__,body = class_info)
        return util.objtojson(response)
# 通过exam_id获取教务班信息
class GetClassByExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin","*")
        params = web.input()
        class_info = Class_model.query('select * from class where cl_id in (select  distinct class_cl_id from \
                     information where exam_ex_id = %s)'%(int(params.ex_id)))
        class_info=[Class_model(**item) for item in class_info]
        response =  util.Response(Status. __success__,body = class_info)
        return util.objtojson(response)

class GetStudentByExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        # args = dict[exam_ex_id:params.ex_id,class_cl_id:params.class_cl_id]
        student_info = Information_model.query('select * from information where exam_ex_id = %s\
             and class_cl_id = %s order by student_st_id'%(params.ex_id,params.class_cl_id))
        student_info = [Information_model(**item) for item in student_info]
        for student in student_info:
            result = Student_model.getByPK(student.student_st_id)
            student['student_name'] = result.st_name
            student['in_state']=util.in_state[int(student.in_state)]
        # args = dict( in_state=0,exam_ex_id=params.ex_id,class_cl_id=params.class_cl_id)
        # not_login_num = Information_model.count(**args)
        result = Information_model.query('select count(*) from information where in_state=%s\
                and class_cl_id=%s and exam_ex_id=%s'%(0,params.class_cl_id,params.ex_id))
        # login_num = Information_model.count(in_state=1)
        response = util.Response(Status.__success__, body=student_info,message=result[0]['count(*)'])
        return util.objtojson(response)

class ConfirmAddStudent(object):#添加单个学生信息,必须的字段为st_id,st_name
    def POST(self):
        web.header("Access-Control-Allow-Origin","*")
        must_params = ('st_id','st_name','cl_id')
        params = web.input()
 
        if util.paramsok(must_params, params) == Status.__params_not_ok__:
                response =  util.Response(Status.__params_not_ok__,message = '参数错误!')
                return util.objtojson(response) 
        st_has_cl = Student_has_class_model(student_st_id = params.st_id,class_cl_id = params.cl_id)
        # del  params.cl_id
        s = Student_model(st_id = params.st_id)
        try:
            st_exist = s.getByArgs(**s)
            if st_exist:
                if st_has_cl.insert():
                    information = model.Information_model.query('select \
                                         distinct(exam_ex_id),sg_id from information where \
                                         class_cl_id = %s' % (params.cl_id))
                    if information != None:
                        information = [model.Information_model(**item) for item in information]
                        for item in information:
                            item.class_cl_id = params.cl_id
                            item.student_st_id = params.st_id
                            item.insert()
                    else:
                        print "none"
                    response =  util.Response(Status. __success__,message = "该学生已添加进课程班级")
                    return util. objtojson(response)
                response =  util.Response(Status. __success__,message = "该学生已存在于课程班级,不能重复添加！")
                return util. objtojson(response)
            else:
                s = Student_model(**params)
                s.insert()
                st_has_cl.insert()
                information = model.Information_model.query('select \
                    distinct(exam_ex_id),sg_id from information where \
                    class_cl_id = %s'%(params.cl_id))
                if information!=None:
                    information = [model.Information_model(**item) for item in information]
                    for item in information:
                        item.class_cl_id = params.cl_id
                        item.student_st_id = params.st_id
                        item.insert()
                else:
                    print "none"
                response =  util.Response(Status. __success__,message = "该学生已添加进课程班级！")
                return util. objtojson(response)
        except Exception as e:
            response =  util.Response(Status. __error__,message = "error")
            return util.objtojson(response)
     
class BatchAddStudent(object):#首先存放excel文件
    def OPTIONS(self):
        web.header("Access-Control-Allow-Origin", "*") 
        web.header("Access-Control-Allow-Methods", "POST, PUT, OPTIONS")
        return True
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*") 
        x = web.input(myfile = {})#获得文件流
        must_params = ('cl_id',)
        file_range = ['xls','xlsx',]
        if util.paramsok(must_params,x) == Status.__params_not_ok__:
              return util.objtojson({"error":"参数错误"})
        # excel_save_site = "../examTransplant1.7/source/excel"
        excel_save_site = student_source
        current_site = os.getcwd()
        print current_site
        current_site =current_site.replace('\\','/')
        real_site =current_site.split('/')
        save_site = excel_save_site.split('/')
        flag = 1
        i = -1
        # print(real_site)
        # print(save_site)
        while i>-4:
            if  real_site[i] != save_site[i]:
                flag = 0
                break
            # print(i)
            i = i -1
        print(flag)
        if flag == 0:
            try:
                os.chdir(excel_save_site)
            except:
                print('os.chdir error')
                os.chdir(current_site)
                return 0
        if 'myfile' in x: 
                filepath=x.myfile.filename.replace('\\','/')
                filename = unicode(filepath.split('/')[-1],'utf-8')
                file_suffix = filename.split('.')[-1]
                file_truth = 0   
                for i in range(len(file_range)):
                    if file_suffix == file_range[i]:
                         file_truth = 1
                if file_truth == 1: 
                    origin_site = os.getcwdu()
                    try:
                        # print(origin_site +'/'+"%s"% filename,'wb+')
                        with open(origin_site +'/'+"%s"% filename,'wb+') as fout:# creates the file where the uploaded file should be stored
                            print('opened')
                            fout.write(x.myfile.file.read()) # writes the uploaded file to the newly created file.
                            print('writed')
                            # fout.close() # closes the file, upload complete.
                            # print('closed')
                            file_site = origin_site +'/'+filename
                    except IOError as err :
                        os.chdir(current_site)
                        return util.objtojson({"error":"文件上传失败!"})
                       
                    try:
                        data = xlrd.open_workbook(file_site)
                        table = data.sheets()[0] 
                        nrows = table.nrows
                        params = dict.fromkeys(Student_model.__attr__)
                        for i in range(5,nrows-1):#行数
                            if i>0:
                                params['st_id']=int(table.row_values(i)[1])
                                params['st_name'] = table.row_values(i)[2]
                                params['st_sex'] = table.row_values(i)[3]
                                params['st_specialty'] = table.row_values(i)[4]
                                params['st_phone'] = table.row_values(i)[5]
                                params['st_picture'] = table.row_values(i)[6]
                                params = Student_model(**params)
                                try: 
                                    params.insert() 
                                    db.insert("student_has_class",student_st_id = params['st_id'],class_cl_id = x.cl_id)
                                except Exception as e:
                                    db.insert("student_has_class",student_st_id = params['st_id'],class_cl_id = x.cl_id)
                        os.chdir(current_site)
                        return 1
                    except:
                       r = {"success":0,"error":"导入数据库失败"}
                       os.chdir(current_site)
                       return util.objtojson(r)
                else:
                    os.chdir(current_site)
                    return 0
        else:
            os.chdir(current_site)
            return 0

class ManageClass:#列出所有教务班，每10组数据一页
    def POST(self):
        web.header("Access-Control-Allow-Origin","*")
        params = web.input()
        count = model.Class_model.count()
        reasurt = model.Class_model.getByPage(int(params.currentPage) - 1)
        page = util.Page(data=reasurt, totalRow=count, currentPage=int(params.currentPage), pageSize=10,
                         status=util.Status.__success__, message="未知")
        response = util.Response(status=util.Status.__success__, body=page)
        return util.objtojson(response)
        # return Class_model.Paging(params.currentPage)
class QueryClass:#查询教务班
    def POST(self):
        mydata = web.input()
        print mydata
        web.header("Access-Control-Allow-Origin", "*")
        must_params = set({'cl_name','currentPage',})
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            print 222
            currentPage = int(mydata.currentPage)-1;
            print mydata.cl_name
            result = orm.db.query('select * from Class where cl_name like \'%%%s%%\'\
                order by cl_id limit %s,%s'%(mydata.cl_name,currentPage*10,10))
            result = [Class_model(**item) for item in result]
            Class = Class_model()
            result1= Class.query('select count(*) from Class where cl_name like \'%%%s%%\''%(mydata.cl_name))
            count = result1[0]['count(*)']
            page = util.Page(data = result, totalRow = count, currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = "未知")
            response = util.Response(status=util.Status.__success__,body=page)
            return util.objtojson(response) 
class UpdateClass:#修改教务班名
    def POST(self):
        must_params = ('cl_name')
        params = web.input()
        if util.paramsok(must_params, params) == Status.__params_not_ok__:
                response =  util.Response(Status.__params_not_ok__)
                return util.objtojson(response)
        
        params = Class_model(**params)
        if params.update():
            response = Response(status = Status.__success__)
            return  util.objtojson(response)
        else:
            response = Response(status = Status.__error__ )
            return  util.objtojson(response)
class AddClass:#增加教务班
    def POST(self):
        web.header("Access-Control-Allow-Origin","*")
        must_params = ('cl_name',)
        params = web.input()
        if util.paramsok(must_params, params) == Status.__params_not_ok__:
            response = Response(status = Status.__params_not_ok__  )
            return  util.objtojson(response)
        params = Class_model(**params)
        try:
            params.insert()
            response = Response(status = Status.__success__)
            return  util.objtojson(response)
        except Exception as e:
            response = Response(status = Status.__error__,message = e)
            return  util.objtojson(response)
class DeleteClass:#删除教务班
    def POST(self):

        web.header("Access-Control-Allow-Origin","*")
        must_params = ('cl_id',)
        mydata = web.input()
        if util.paramsok(must_params, mydata) == Status.__params_not_ok__:
            response = Response(status = Status.__params_not_ok__ ,message = "参数错误!")
            return  util.objtojson(response)
        params = Class_model(cl_id = mydata.cl_id)
        teacher = model.Teacher_model.getByArgs(tc_level='管理员')
        if str(mydata.deletepassword) != teacher[0].tc_password:
            response = util.Response(status=util.Status.__error__,message = "密码错误")
            return util.objtojson(response)
        try:
            with orm.db.transaction():
                db.delete('student_has_class', where="class_cl_id = $class_cl_id", vars={'class_cl_id': params.cl_id, })
                if db.delete('class', where="cl_id = $cl_id", vars={'cl_id': params.cl_id, }):
                    response = Response(status=Status.__success__, message="班级删除成功!")
                    return util.objtojson(response)
                else:
                    response = Response(status=Status.__error__, message="班级删除失败!")
                    return util.objtojson(response)
        except Exception as e:
            util.getFileRotatingLog().debug(e)
            response = Response(status=Status.__error__, message="班级删除失败!")
            return util.objtojson(response)
       
class OpenClass:
    def POST(self):
        web.header("Access-Control-Allow-Origin","*")
        must_params = ('cl_id',)
        params = web.input(requestPage='0')
        if util.paramsok(must_params, params) == Status.__params_not_ok__:
                    response = Response(status = Status.__params_not_ok__  )
                    return  util.objtojson(response)
        requestPage = params['requestPage'].encode('utf-8')
        del params['requestPage']
        #根据班号查学号，根据学号查学生
        st_has_cl = Student_has_class_model(class_cl_id = params.cl_id)
        st_has_cl_result = Student_has_class_model.getByPage(page = requestPage,**st_has_cl)
        if st_has_cl_result:
            final_result = list() 
            for s in range(len(st_has_cl_result)):
                  st_ = st_has_cl_result[s].get('student_st_id')
                  st  = Student_model(st_id = st_)
                  st_result = Student_model.getByPage(page = requestPage,**st)
                  final_result.append(st_result[0])
            response = Response(status = Status.__success__,body = final_result)
            return util.objtojson(response)
        else:
             response = Response(status = Status.__obj_null__)
             return util.objtojson(response)
class DeleteStudent:
    def POST(self):
        web.header("Access-Control-Allow-Origin","*")
        must_params = ('st_id','cl_id')
        params = web.input()
        if util.paramsok(must_params, params) == Status.__params_not_ok__:
            response = Response(status = Status.__params_not_ok__  )
            return  util.objtojson(response)
        class_result = db.query("SELECT * FROM  class WHERE cl_id= $cl_id", vars={'cl_id':params.cl_id})
#         cl_id = class_result. __getitem__(0).get('cl_id')
        try:
            r1 = db.delete('student_has_class', where='class_cl_id=$cl_id and student_st_id = $st_id', vars={'cl_id':params.cl_id,'st_id':params.st_id})
            r2 = db.delete('information',where = 'student_st_id=$st_id and class_cl_id = $cl_id',vars={'st_id':params.st_id,'cl_id':params.cl_id})
            r3 = db.delete('student', where='st_id=$st_id', vars={'st_id':params.st_id})
            
            if r1:
                if r3:
                    response = Response(status = Status.__success__,message = "该学生已完全删除!")
                    return  util.objtojson(response)
                response = Response(status = Status.__success__,message = "该学生已从该课程班删除!")
                return  util.objtojson(response)
            else:
                response = Response(status = Status.__success__,message = "该学生已从该课程班删除!")
                return  util.objtojson(response)
        except Exception as e:
                response = Response(status = Status.__system_exception__,message = "该学生存在于其他课程班，已从当前课程班删除!")
                return  util.objtojson(response)
            
class CheckStudent:#修改学生
    def POST(self):
        web.header("Access-Control-Allow-Origin","*")
        must_params = ('st_id',)
        params = web.input()
        if util.paramsok(must_params, params) == Status.__params_not_ok__:
            response = Response(status = Status.__params_not_ok__  )
            return  util.objtojson(response)
        st_modify  = Student_model(**params)
        result = st_modify.update()
        if result:
            response = Response(status = Status.__success__)
            return util.objtojson(response)
        else:
            response = Response(status = Status.__error__)
            return util.objtojson(response)

        
class QueryStudent: 
    def POST(self):
        web.header("Access-Control-Allow-Origin","*")
        must_params = ('st_id','cl_name')
        params = web.input()   
        if util.paramsok(must_params, params) == Status.__params_not_ok__:
            response = Response(status = Status.__params_not_ok__  )
            return  util.objtojson(response)
        class_result = db.query("SELECT * FROM  class WHERE cl_name= $cl_name", vars={'cl_name':(params.cl_name.encode('utf-8'))})
        if class_result:
             cl_id = class_result. __getitem__(0).get('cl_id')
             st_has_class_result = db.query("SELECT * FROM  student_has_class WHERE class_cl_id= $cl_id", vars={'cl_id':cl_id})
             if st_has_class_result:
                 st = Student_model(st_id = params.st_id)
                 st_result = Student_model.getByArgs(**st)
                 if st_result == list():
                     response = Response(status = Status.__obj_null__ ,body = st_has_class_result)
                     return util.objtojson(response)
                 response = Response(status = Status.__success__,body = st_result)
                 return util.objtojson(response)
             else:
                response = Response(status = Status.__obj_null__ ,body = st_has_class_result)
                return util.objtojson(response)
                 
        else:
             response = Response(status = Status.__obj_null__)
             return util.objtojson(response)
                  

app = web.application(urls,globals())

    
    
    
    
    