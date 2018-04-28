import sys
import web  

urls = (  
    '/(.*)', 'hello'  
)  
  
app = web.application(urls, globals(), autoreload = True) 
  
class hello:  
    def GET(self, name):  
        return 'Version: ' + sys.version + '!'  

application = app.wsgifunc()
