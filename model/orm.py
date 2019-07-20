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
    def __init__(self, names=(), values=(), **kw):    # 初始化
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):                 # 获取参数
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):           # 设置参数
        self[key] = value


class Model(Dict):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)           # 父类的初始化

    @classmethod
    def getByPK(cls, PK):               # 通过主键来获取对象
        myvar = dict(myPK=PK)
        result = db.select(cls.__table__, vars=myvar, where='%s=$myPK' % cls.__pk__)
        print(result)
        return cls(**result[0]) if result else None

    @classmethod
    def getByArgs(cls, **args):         # 根据参数来获取对象完整数据
        myvar = args
        mywhere = ''
        for k, v in args.items():
            if k not in cls.__attr__:           # 如果该对象的属性中没有这个关键字，则返回None
                print('no attribute <%s> in table %s' % (k, cls.__table__))
                return None
            mywhere += '%s=$%s ' % (k, k)
        if mywhere != '':
            result = db.select(cls.__table__, vars=myvar, where=mywhere)
        else:
            result = db.select(cls.__table__)
        return [cls(**item) for item in result]      # 以字典的形式返回这个对象的所有属性

    @classmethod
    def getByPage(cls, page, **args):  # 根据页码查询数据库，start query from page 0
        myvar = args
        mywhere = ''
        for k, v in args.items():
            if k not in cls.__attr__:
                print('no attribute <%s> in table %s' % (k, cls.__table__))
                return None
            mywhere += '%s=$%s ' % (k, k)
        myoffset = page * cls.__countperpage__
        if mywhere != '':                                   # 查询条件不为空时按条件查询
            result = db.select(cls.__table__, vars=myvar, where=mywhere)        # 数据库查询， table_name, vars填充查询条件
        else:                                               # 查询条件为空时按页码返回10条数据
            result = db.select(cls.__table__, limit=cls.__countperpage__, offset=myoffset)
        return [cls(**item) for item in result]

    @classmethod
    def Paging(self, currentPage):     # 在当前页基础上翻页，返回数据
        # must_params =set({'currentPage'})
        # if(util.paramsok(must_params, currentPage) == 2):
        #     response = util.Response(status=util.Status.__params_not_ok__)
        #     return util.objtojson(response)
        # else:
        count = self.count()            # 返回数据表记录的总数
        reasurt = self.getByPage(int(currentPage) - 1)          # 获取记录列表（currentPage=1时，返回0-9条记录）
        page = util.Page(data=reasurt, totalRow=count, currentPage=int(currentPage), pageSize=10,
                         status=util.Status.__success__, message="未知")          # Page实例化
        response = util.Response(status=util.Status.__success__, body=page)
        return util.objtojson(response)

    @classmethod
    def count(cls, **args):             # 按条件查询数据库，字典args填充查询条件，返回符合条件的记录个数，条件为空时返回数据表记录的总数，用于分页
        myvar = args
        mywhere = ''
        for k, v in args.items():
            if k not in cls.__attr__:
                print('no attribute <%s> in table %s' % (k, cls.__table__))
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
        return results           # 返回字典

    def insert(self):            # 向数据库插入数据
        params = {}
        for k in self.__insertable__:
            if k in self:                   # self为传入的对象，如果插入到数据在传入的对象中没有，并且该数据在数据库中又不能为空，则插入失败
                params[k] = self[k]         # 获取需要插入到数据库中的数据
            elif k in self.__notnull__:
                print('%s can not be set NULL, while insert into %s' % (k, self.__table__))
                return

        try:
            db.insert(self.__table__, **params)     # 将数据插入到数据库
        except Exception as e:                      # 插入失败则抛出异常
            print('insert table %s failed,<%s>' % (self.__table__, e))
            return False
        return True

    def insertBackid(self):     # 向数据库插入数据，兵返回主键的最大值
        params = {}
        for k in self.__insertable__:
            if k in self:
                params[k] = self[k]
            elif k in self.__notnull__:
                print('%s can not be set NULL, while insert into %s' % (k, self.__table__))
                return

        try:
            with db.transaction():      # 数据库事务，当整个过程不完全执行时，则回滚
                db.insert(self.__table__, **params)
                reasult = db.query('select max(%s) from %s' % (self.__pk__, self.__table__))
        except Exception as e:
            print('insert table %s failed,<%s>' % (self.__table__, e))
            return False
        return reasult

    def delete(self):   # 尽量避免删除操作。根据对象的主键删除整条记录
        try:
            db.delete(self.__table__, where='%s=%s' % (self.__pk__, self[self.__pk__]))
        except Exception as e:
            print('delete table %s failed,<%s>' % (self.__table__, e))
            return False
        return True

    def update(self):   # 根据对象的数据来更新数据库
        params = {}
        for k in self.__updateable__:
            if k in self:
                params[k] = self[k]
        result = 0
        try:
            db.update(self.__table__, where='%s=%s' % (self.__pk__, self[self.__pk__]), **params)
        except Exception as e:
            print('update table %s failed,<%s>' % (self.__table__, e))
            return False
        return True

    def updateOrInsert(self):   # 更新或插入数据库，当两者都执行失败时，返回False
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

