#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
import os
import shutil
urls = (
    '/','index',
)


class index:
    def GET(self):
        # web.seeother('/static/'+'login.html')
        #try:
         #   os.mkdir(u'test')
        #except:
         #   shutil.rmtree(u'test')
        os.mkdir(u'/var/www/test')
        with open(u'/var/www/test/write.txt', 'w') as f:
            f.write('xeshi')
        return os.getcwd()
app = web.application(urls, globals(), autoreload = True)
application = app.wsgifunc()
