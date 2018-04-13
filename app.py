# -*- coding: UTF-8 -*-
import json
from datetime import datetime
from sqlalchemy import and_,or_
import tornado.ioloop
import tornado.web
import orm
from orm import User
#----------------------------------------------------------------------------------------------------------
#-------------------------------------------- there is database --------------------------------------------
#----------------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------------
#-------------------------------------------- there is handler --------------------------------------------
#----------------------------------------------------------------------------------------------------------

class BaseHandle(tornado.web.RequestHandler):
    def initialize(self):
        self.session = orm.SessionType()

    def get_current_user(self):
        return self.get_secure_cookie("username")

    def on_finish(self):
        self.session.close()

class IndexHandler(BaseHandle):
    def get(self):
        #self.session.add(User(name="wll",password="12345",mail="444@qq.com",regdate="2018-04-03 21:27:55",sex=True,mobile="13875987564"))
        #self.session.commit()
        self.render("index.html",TitleNum = range(3),TimeLineNum = range(6))

class AboutHandler(BaseHandle):
    def get(self):
        self.render("about.html",ItemNum = ["n1","n2","n3","n4","n5"])

class LifeHandler(BaseHandle):
    def get(self):
        self.render("slowlife.html",PhoneNum = range(8))

class ShareHandler(BaseHandle):
    def get(self):
        self.render("share.html",GroupData = range(8))

class LearnHandler(BaseHandle):
    def get(self):
        self.render("learn.html",GroupData = range(6),TimeLineNum = range(6))

class BBSHandler(BaseHandle):
    def get(self):
        self.render("bbs.html",MessageNum = range(6))

class ManageHandler(BaseHandle):
    # 如果get_current_user（）返回的值不为真，则跳转到"login_url":"/login"中
    @tornado.web.authenticated
    def get(self):
        pass

    def post(self, *args, **kwargs):
        return False

class LoginHandler(BaseHandle):
    def get(self):
        self.render("login.html")

    def post(self):
        #可以在这设置响应头信息
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')
        # 此处的'username'对应ajax里的data:{username:value}的username,即字典的键
        data = {'status': False, 'message': '用户名或密码错误，请重新输入！', 'url': "/login"}  # 封装数据
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        print("Ajax Post:" + username + "密码为:" + password)
        result = self.session.query(User).filter(User.name == username,User.password == password).first()
        #如果用户存在，则返回User对象
        if result:
            data['status'] = True
            data["message"] = "successfully"
            data["url"] = "/index"
            self.set_secure_cookie("username", result.name)
            print("当前登录用户为：" + result.name + "    密码：" + result.password)
        #将data序列化为JSON回传给前端
        self.write(json.dumps(data))


class RegisterHandler(BaseHandle):
    def get(self):
        self.render("register.html")

    def post(self):
        data = {'status': False, 'message': '信息填写错误，请重新输入！', 'url': "/login"}  # 封装数据
        target = self.get_argument("target", None)
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        phone_number = self.get_argument("phone_number", None)
        email = self.get_argument("email", None)
        #先处理单独项目Ajax提交
        #如果需要查询username，则判断数据库中是否已存在
        if target == "username":
            if self.session.query(User).filter(User.name == username).first():
                self.write("false")
            else:
                self.write("true")
            return self.finish()  # 如果不加这一段，还会执行下面的语句，类似break
        # 处理from提交,validate已经确保用户名合法且不重复
        if not target and username and password and phone_number and email:
            self.session.add(User(name=username, password=password, mail=email, regdate=datetime.now(),mobile=phone_number))
            self.session.commit()
            #更新传递给前端的信息
            data['status'] = True
            data['message'] = "注册成功，请您重新登录，正在为您跳转…………"
            self.write(json.dumps(data))


#----------------------------------------------------------------------------------------------------------
#-------------------------------------------- there is modules --------------------------------------------
#----------------------------------------------------------------------------------------------------------
class IndexImageHeadModule(tornado.web.UIModule):
    def render(self, item):
        data = {
            "image_name":"t03.jpg",
            "image_describe":"点击查看详情",
            "text_title":"永不落幕的协奏曲",
            "text_content":"让世界拥有它的脚步，让我保有我的茧。当溃烂已极的心灵再不想做一丝一毫的思索时，就让我静静回到我的茧内，以回忆为睡榻，以悲哀为覆被，这是我唯一的美丽。",
        }
        return self.render_string("modules\IndexImageHead.html",data=data)

class TimeLineModule(tornado.web.UIModule):
    def render(self, item):
        data = {
            "month_day":"03-31",
            "year":"2018",
            "title":"三步实现螺旋上天的唯美效果",
            "image":"t02.jpg",
            "content":"现在很多网站都有这种效果，我就整理了一下，分享出来。利用滚动条来实现动画效果，ScrollReveal.js 用于创建和管理元素进入可视区域时的动画效果，帮助你的网站增加吸引力...。",
        }
        return self.render_string("modules\TimeLine.html",data=data)

class AboutTimeLineModul(tornado.web.UIModule):
    def render(self, clas):
        data = {
            "class":clas,
            "target":"/index",
            "year":"2018",
            "tital":"喝心灵鸡汤的人",
        }
        return self.render_string("modules\AboutTimeXAxis.html",data=data)

class SlowLifePhoneModul(tornado.web.UIModule):
    def render(self, clas):
        data = {
            "phone":"girl.jpg",
            "content":"/index",
        }
        return self.render_string("modules\SlowLifePhone.html",data=data)

class LearnGroupModul(tornado.web.UIModule):
    def render(self, clas):
        data = {
            "target":"/index",
            "content":"心得笔记",
        }
        return self.render_string("modules\LearnGroup.html",data=data)

class MessageModul(tornado.web.UIModule):
    def render(self, clas):
        data = {
            "target":"/index",
            "phone":"girl.jpg",
            "message":"当您驻足停留过，从此便注定我们的缘分。站在时间的尽头，我们已是朋友，前端的路上我再也不用一个人独自行走。",
        }
        return self.render_string("modules\BBSMessage.html",data=data)

#----------------------------------------------------------------------------------------------------------
#-------------------------------------------- there is initial --------------------------------------------
#----------------------------------------------------------------------------------------------------------

settings = {
    'template_path': 'templates',  # html文件模板路径配置
    'static_path': 'static',# css,js文件路径配置
    'autoreload': True,
    'ui_modules' :{'IndexImageHead': IndexImageHeadModule,
                    "IndexTimeLine":TimeLineModule,
                    "AboutTimeLine":AboutTimeLineModul,
                    "SlowLifePhone":SlowLifePhoneModul,
                    "LearnGroup":LearnGroupModul,
                    "Message":MessageModul,
                   },
    "login_url":"/login",
    "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
    "debug":True,
}

application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/about", AboutHandler),
    (r"/slowlife", LifeHandler),
    (r"/share", ShareHandler),
    (r"/learn", LearnHandler),
    (r"/bbs", BBSHandler),
    (r"/manage", ManageHandler),
    (r"/login", LoginHandler),
    (r"/register", RegisterHandler),
],**settings)

if __name__ == "__main__":
    #初始化数据库
    orm.Base.metadata.create_all(orm.engine)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()