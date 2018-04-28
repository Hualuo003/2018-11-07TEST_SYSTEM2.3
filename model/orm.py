#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import web
from config import configs
# import util



sys.path.append('../')

db = web.database(host=configs.db.host, port=configs.db.port, dbn='mysql', db=configs.db.database, user=configs.db.user,
                  pw=configs.db.password)


# def GetByQt_type(qt_type,qt_id):
#     # myvar = dict(qt_id = qt_id)
#     print qt_type
#     # result = db.select(qt_type,vars=myvar,where='qt_id =$qt_id')
#     # print result
#     return qt_type

class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


class Model(Dict):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    @classmethod
    def getByPK(cls, PK):
        myvar = dict(myPK=PK)
        result = db.select(cls.__table__, vars=myvar, where='%s=$myPK' % cls.__pk__)
        print result
        return cls(**result[0]) if result else None

    @classmethod
    def getByArgs(cls, **args):
        myvar = args
        mywhere = ''
        for k, v in args.iteritems():
            if k not in cls.__attr__:
                print 'no attribute <%s> in table %s' % (k, cls.__table__)
                return None
            mywhere += '%s=$%s ' % (k, k)
        if mywhere != '':
            result = db.select(cls.__table__, vars=myvar, where=mywhere)
        else:
            result = db.select(cls.__table__)
        return [cls(**item) for item in result]

    @classmethod
    def getByPage(cls, page, **args):  # start query from page 0
        myvar = args
        mywhere = ''
        for k, v in args.iteritems():
            if k not in cls.__attr__:
                print 'no attribute <%s> in table %s' % (k, cls.__table__)
                return None
            mywhere += '%s=$%s ' % (k, k)
        myoffset = page * cls.__countperpage__
        if mywhere != '':
            result = db.select(cls.__table__, vars=myvar, where=mywhere)
        else:
            result = db.select(cls.__table__, limit=cls.__countperpage__, offset=myoffset)
        return [cls(**item) for item in result]

    @classmethod
    def Paging(self, currentPage):
        # must_params =set({'currentPage'})
        # if(util.paramsok(must_params, currentPage) == 2):
        #     response = util.Response(status=util.Status.__params_not_ok__)
        #     return util.objtojson(response)
        # else:
        count = self.count()
        reasurt = self.getByPage(int(currentPage) - 1)
        page = util.Page(data=reasurt, totalRow=count, currentPage=int(currentPage), pageSize=10,
                         status=util.Status.__success__, message="未知")
        response = util.Response(status=util.Status.__success__, body=page)
        return util.objtojson(response)

    @classmethod
    def count(cls, **args):
        myvar = args
        mywhere = ''
        for k, v in args.iteritems():
            if k not in cls.__attr__:
                print 'no attribute <%s> in table %s' % (k, cls.__table__)
                return None
            mywhere += '%s=$%s ' % (k, k)
        if mywhere != '':
            result = db.query('select count(*) as mycount from %s where %s' % (cls.__table__, mywhere), vars=myvar)
        else:
            result = db.query('select count(*) as mycount from %s ' % cls.__table__)
        return result[0]['mycount']

    @classmethod
    def query(sql_query, vars):  # 进行复杂查询的时候使用，尽量不要用，破坏设计
        results = db.query(vars)
        return results

    def insert(self):
        params = {}
        for k in self.__insertable__:
            if k in self:
                params[k] = self[k]
            elif k in self.__notnull__:
                print '%s can not be set NULL, while insert into %s' % (k, self.__table__)
                return

        try:
            db.insert(self.__table__, **params)
        except Exception, e:
            print 'insert table %s failed,<%s>' % (self.__table__, e)
            return False
        return True

    def insertBackid(self):
        params = {}
        for k in self.__insertable__:
            if k in self:
                params[k] = self[k]
            elif k in self.__notnull__:
                print '%s can not be set NULL, while insert into %s' % (k, self.__table__)
                return

        try:
            with db.transaction():
                db.insert(self.__table__, **params)
                reasult = db.query('select max(%s) from %s' % (self.__pk__, self.__table__))
        except Exception, e:
            print 'insert table %s failed,<%s>' % (self.__table__, e)
            return False
        return reasult

    def delete(self):  # 尽量避免删除操作 Avoid delete-operation as much as you can
        try:
            db.delete(self.__table__, where='%s=%s' % (self.__pk__, self[self.__pk__]))
        except Exception, e:
            print 'delete table %s failed,<%s>' % (self.__table__, e)
            return False
        return True

    def update(self):
        params = {}
        for k in self.__updateable__:
            if k in self:
                params[k] = self[k]
        result = 0
        try:
            db.update(self.__table__, where='%s=%s' % (self.__pk__, self[self.__pk__]), **params)
        except Exception, e:
            print 'update table %s failed,<%s>' % (self.__table__, e)
            return False
        return True

    def updateOrInsert(self):
        if self.insert():
            return True
        elif self.update():
            return True
        else:
            return False




            # @classmethod
            # def addquestion(self,question):
            #     t = db.transaction()
            #     choice = model.Choice_model()
            #     try:
            #         self.insert()
            #         reasurt = self.query('select max(qt_id) from question')
            #         choice.question_qt_id = reasurt[0]['max(qt_id)']
            #         choice = model.choice_model(**question)
            #         choice.insert()
            #     except:
            #         t.rollback()
            #         print choice
            #         print self
            #         return choice
            #     else:
            #         t.commit()
            # return choice




            # with db.transaction():
            #     self.insert()
            #     reasurt = self.query('select max(qt_id) from question')
            #     choice.question_qt_id = reasurt[0]['max(qt_id)']
            #     choice.insert()
            #     return choice


if __name__ == '__main__':
    util.test(db, '1.py')

