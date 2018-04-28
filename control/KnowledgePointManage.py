#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import util
sys.path.append('../')
from config import configs
from model import model

import web

urls = (
    '/','index',
    'AddKnowledgePoint/','AddKnowledgePoint',
    'UpdataKnowledgePoint/','UpdataKnowledgePoint',
    'RequestKnowledgePoint/','RequestKnowledgePoint',
    'DeleteKnowledgePoint/','DeleteKnowledgePoint',
    'SelectKnowledge/','SelectKnowledge',
    
)
class index:
    def GET(self):
        mydata = web.input(name=None)
        return 'KnowledgePoint page'
    def POST(self):
        mydata = web.input(name=None)
        return 'KnowledgePoint page'



# 添加知识点
class AddKnowledgePoint:
    def GET(self):
        return 'AddKnowledgePoint'
    def POST(self):
        mydata = web.input()
        kp = model.Knowledge_model()
        must_params = kp.__notnull__
        web.header("Access-Control-Allow-Origin", "*") 
        if(util.paramsok(must_params, mydata) == 2):
            response = util.Response(status=util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            kp = model.Knowledge_model(**mydata)
            if kp.insert():
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)
# 返回知识点
class RequestKnowledgePoint:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        mydata = web.input()
        Knowledge = model.Knowledge_model()
        result = Knowledge.getByArgs()
        KnowledgeData = Knowledge.getByPage(int(mydata.currentPage)-1)
        page = util.Page(data = KnowledgeData, totalRow = len(result), currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = "未知")
        response = util.Response(status=util.Status.__success__,body=page)
        return util.objtojson(response)


# 修改知识点名称
class UpdataKnowledgePoint:
    def POST(self):
        mydata = web.input()
        print mydata
        kp = model.Knowledge_model()
        must_params = kp.__notnull__
        web.header("Access-Control-Allow-Origin", "*") 
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        else:
            kp = model.Knowledge_model(**mydata)
            if kp.update():
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)

class DeleteKnowledgePoint:
    def POST(self):
        mydata = web.input()
        kp = model.Knowledge_model()
        must_params = set ({'kl_id'})
        web.header("Access-Control-Allow-Origin", "*") 
        if(util.paramsok(must_params,mydata) == 2):
            response = util.Response(status = util.Status.__params_not_ok__)
            return util.objtojson(response)
        elif str(mydata.deletepassword) == '123456':
            kp.kl_id = mydata.kl_id
            print kp.kl_id
            if kp.delete():
                response = util.Response(status=util.Status.__success__)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__)
                return util.objtojson(response)
        response = util.Response(status=util.Status.__error__)
        return util.objtojson(response)


class SelectKnowledge:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        mydata = web.input()
        print mydata
        Knowledge = model.Knowledge_model()
        result = Knowledge.getByArgs(kl_name = mydata.kl_name)
        page = util.Page(data = result, totalRow = len(result), currentPage = int(mydata.currentPage), pageSize = 10, status=util.Status.__success__, message = "未知")
        print len(result)
        response = util.Response(status=util.Status.__success__,body=page)
        return util.objtojson(response)




        

app = web.application(urls,globals())
render = web.template.render('template')
if __name__ == '__main__':
    
    if len(urls)&1 == 1:
        print "urls error, the size of urls must be even."
    else:
        app.run()