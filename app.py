# -*- coding: UTF-8 -*-
import json
import platform
from datetime import datetime
from sqlalchemy import func
import tornado.web
import orm
from orm import User,Article
import os,sys
import hashlib                      #用于md5加密
from PIL import Image               #用于图片处理
#----------------------------------------------------------------------------------------------------------
#-------------------------------------------- there is database --------------------------------------------
#----------------------------------------------------------------------------------------------------------
CATEGORY = [{"category": "python", "url": "/learn"},
            {"category": "JavaScript/CSS", "url": "/learn"},
            {"category": "Tornado", "url": "/learn"},
            {"category": "Sqlalchemy", "url": "/learn"},
            {"category": "第三方插件", "url": "/learn"}
            ]
categoryCheck = [["checked", "", "", "", "", ""],
                  ["", "checked", "", "", ""],
                  ["", "", "checked", "", ""],
                  ["", "", "", "checked", ""],
                  ["", "", "", "", "checked"],
                  ]
visibilitySelect = [["checked", ""],
                    ["", "checked"],
                    ]

#----------------------------------------------------------------------------------------------------------
#-------------------------------------------- there is handler --------------------------------------------
#----------------------------------------------------------------------------------------------------------

class BaseHandle(tornado.web.RequestHandler):
    def initialize(self):
        self.session = orm.SessionType()

    def get_current_user(self):
        user = self.session.query(User).filter(User.name == self.get_secure_cookie("username")).first()
        if user:
            self.currentuser = self.get_secure_cookie("username")
            self.user = self.session.query(User).filter(User.name == self.currentuser).first()
            print("BaseHandle："+self.user.name)
            return True
        return False


    def on_finish(self):
        self.session.close()

class IndexHandler(BaseHandle):
    def get(self):
        #self.session.add(User(name="wll",password="12345",mail="444@qq.com",regdate="2018-04-03 21:27:55",sex=True,mobile="13875987564"))
        #self.session.commit()
        allArticles = []
        articles = self.session.query(Article).all()
        for article in articles:
            tempList = {}
            tempList["id"] = article.id
            tempList["title"] = article.title
            tempList["describe"] = article.describe
            tempList["category"] = article.category
            # 留言数还没实现，先用0表示
            tempList["date"] = article.date
            tempList["pictuername"] = article.pictuername
            allArticles.append(tempList)
        self.render("index.html",TitleNum = range(3),Articles = allArticles)

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
        allArticles = []
        articles = self.session.query(Article).all()
        for article in articles:
            tempList = {}
            tempList["id"] = article.id
            tempList["title"] = article.title
            tempList["describe"] = article.describe
            tempList["category"] = article.category
            # 留言数还没实现，先用0表示
            tempList["date"] = article.date
            tempList["pictuername"] = article.pictuername
            allArticles.append(tempList)
        self.render("learn.html",categories = CATEGORY,Articles = allArticles)

class BBSHandler(BaseHandle):
    def get(self):
        self.render("bbs.html",MessageNum = range(6))

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
            data["url"] = "/system/index"
            self.set_secure_cookie("username", result.name)
            #登陆次数+1
            result.loginnum = result.loginnum + 1
            #更新最后一次登录时间
            result.lasttime = result.curtime
            result.curtime = datetime.now()
            # 更新最后一次登录IP
            result.lastip = result.curip
            result.curip = self.request.remote_ip
            print("当前登录用户为：" + result.name + "    密码：" + result.password)
            self.session.commit()
        #将data序列化为JSON回传给前端
        self.write(json.dumps(data))

class LogoutHandler(BaseHandle):
    def get(self):
        self.clear_cookie("username")
        #self.set_secure_cookie("username", None)
        self.render("index.html", TitleNum=range(3), TimeLineNum=range(6))

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


class SystemIndexHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):

        UA = self.request.headers["User-Agent"]
        print("CurrentIP:" + (self.request.remote_ip))
        print("CurrentUser:" + (self.user.name))
        windows = "无法识别的操作系统"
        Windows = {
            "Windows NT 10.0":"Windows 10",
            "Windows NT 6.4": "Windows 10",
            "Windows NT 6.3": "Windows 8.1",
            "Windows NT 6.2": "Windows 8",
            "Windows NT 6.0": "Windows 8",
            "Windows NT 6.1": "Windows 7",
            "Windows NT 5.1": "Windows XP",
        }
        browser = "无法识别的浏览器"
        Browser = {
            "SogouMobileBrowser": "搜狗手机浏览器",
            "UCBrowser": "UC浏览器",
            "UCWEB": "UC浏览器",
            "Opera": "Opera浏览器",
            "QQBrowser": "QQ浏览器",
            "TencentTraveler": "QQ浏览器",
            "MetaSr": "搜狗浏览器",
            "360SE": "360浏览器",
            "The world": "世界之窗浏览器",
            "Maxthon": "遨游浏览器",
            "Chrome":"Chrome浏览器",
            "safari":"Safari浏览器",
            "Firefox":"Firefox浏览器"
        }
        #判断操作系统版本
        for os in Windows:
            if UA.find(os) != -1:
                windows = Windows[os]
                break
        # 判断操作浏览器版本
        for name in Browser:
            if UA.find(name) != -1:
                browser = Browser[name]
                break
        admin_num = self.session.query(User).filter(User.admin == True).count()
        member_num = self.session.query(func.count(User.id)).first()[0]
        current_ip = self.request.remote_ip
        time = datetime.now()
        self.render("backstage\index.html",current_user = self.currentuser,login_num = self.user.loginnum,mail = self.user.mail,
                    phone = self.user.mobile,last_time = self.user.lasttime,last_ip = self.user.lastip,admin_num = admin_num,
                    browser = browser,python_version = platform.python_version(),os = windows,member_num = member_num,
                    current_ip = current_ip,time = time)


class SystemLearningHandler(BaseHandle):
    CategorySelect=["Python","JavaScript/CSS","Tornado","Sqlalchemy","第三方插件"]
    @tornado.web.authenticated
    def get(self):
        allArticles = []
        #如果当前用户为管理员，则显示所有人的文章
        if(self.session.query(User).filter(User.name == self.currentuser,User.admin == True).first()):
            print("当前是管理员，显示所有文章")
            articles = self.session.query(Article).all()
            #获得文章数量
            articlesNum = len(articles)
        else:
            print("当前是普通用户，只显示个人文章")
            articles = self.session.query(Article).filter(Article.userName == self.currentuser).all()
            # 获得文章数量
            articlesNum = len(articles)
        for article in articles:
            tempList = {}
            #print(article.title)
            #print(article.category)
            #print(article.keywork)
            #print(article.date)
            tempList["id"] = article.id
            tempList["title"] = article.title
            tempList["category"] = self.CategorySelect[article.category]
            tempList["keywork"] = article.keywork
            # 留言数还没实现，先用0表示
            tempList["msg"] = 0
            tempList["date"] = article.date
            allArticles.append(tempList)
        self.render(r"backstage\learning.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                    articlesNum = articlesNum,articles = allArticles)

class SystemArticleAddPageHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        self.render(r"backstage\add-article.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                    article_status = "未发表",article_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )

class SystemAddArticleHandler(BaseHandle):
    @tornado.web.authenticated
    def post(self):
        title = self.get_argument("title")
        content = self.get_argument("content")
        describe = self.get_argument("describe")
        category = self.get_argument("category")
        keywork = self.get_argument("keywork")
        password = self.get_argument("password")
        visibility = self.get_argument("visibility")
        pictuerName = self.get_argument("pictuername")
        #print(title + "------" + content + "------" + describe + "------" + category + "------" + keywork + "------" + password + "------" + visibility + "------" + pictuerName)
        #将文章内容存储到数据库中
        self.session.add(Article(userName = self.user.name,title = title,content = content,describe = describe,
                                 category = category,keywork = keywork,password = password,visibility = visibility,
                                 pictuername = pictuerName,date = datetime.now()))
        self.session.commit()
        data = {'message': '文章已发表成功！', 'url': "/system/learning"}  # 封装数据
        #回传AJAX结果
        self.write(json.dumps(data))


class SystemFileUploadHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        self.render(r"backstage\add-article.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                    )
    @tornado.web.authenticated
    def post(self):
        #这里的属性名要和html中的name一样
        FileData =  self.request.files["input-file"]
        for file in FileData:
            print(file)
            #filetype = file["content_type"]
            #filename = file["filename"]
            filebody = file["body"]
            filehash = hashlib.md5(filebody).hexdigest()
            #print(hashlib.md5((self.user.name + datetime.now().strftime("%Y%m%d%H%M%S") + filehash).encode('utf-8')).hexdigest())
            #获得发送来的文件后缀名
            filesuffix = os.path.splitext(file["filename"])[1]
            #设置存储图片路径,文件命名方式：用户名 + 日期 + hash值 + 目前已有文章数量
            articleNum = self.session.query(Article).count()
            filename = hashlib.md5((self.user.name + datetime.now().strftime("%Y%m%d%H%M%S") + filehash + str(articleNum)).encode('utf-8')).hexdigest() + filesuffix
            filepath = os.path.join(sys.path[0],"static","images","articlecover",filename)
            print(filepath)
            with open(filepath, 'wb') as f:
                f.write(filebody)
            try:
                image = Image.open(filepath)
                image.resize((300, 256))
                image.save(filepath)
            except IOError:
                print("cannot create thumbnail for", filepath)

            #将保存的文件名回传回去(JSON格式)
            self.write({"msg":"文章发布成功！","pictuer":filename,"url":"/system/learning"})

class SystemUpdateArticleHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self,id):
        tagArticle = self.session.query(Article).filter(Article.id == id).first()
        #确定存在该id的文章
        if tagArticle:
            title = tagArticle.title
            content = tagArticle.content
            describe = tagArticle.describe
            category = categoryCheck[tagArticle.category]
            keywork = tagArticle.keywork
            passwork = tagArticle.password
            visibility = visibilitySelect[tagArticle.visibility]
            date = tagArticle.date
            self.render(r"backstage\update-article.html",article_title = title,article_content = content,
                        article_describe = describe,article_category = category,article_keywork = keywork,
                        article_passwork = passwork,article_visibility = visibility,article_date = date,
                        article_id = id,
                        current_user=self.currentuser, mail=self.user.mail, phone=self.user.mobile,
                        )

    @tornado.web.authenticated
    def post(self, id):
        tagArticle = self.session.query(Article).filter(Article.id == id).first()
        # 确定存在该id的文章
        if tagArticle:
            tagArticle.title = self.get_argument("title")
            tagArticle.content = self.get_argument("content")
            tagArticle.describe = self.get_argument("describe")
            tagArticle.category = self.get_argument("category")
            tagArticle.keywork = self.get_argument("keywork")
            tagArticle.password = self.get_argument("password")
            tagArticle.visibility = self.get_argument("visibility")
            tagArticle.date = datetime.now()
            #将文章内容更新到数据库中
            self.session.commit()
            data = {'message': '文章已更新成功！', 'url': "/system/learning"}  # 封装数据
            #回传AJAX结果
            self.write(json.dumps(data))

class SystemDeleteArticleHandler(BaseHandle):
    #get用于处理单个删除请求
    @tornado.web.authenticated
    def get(self,cls):
        tagArticle = self.session.query(Article).filter(Article.id == cls).first()
        #确定存在该id的文章
        if tagArticle:
            #先删除图片再删除数据
            filepath = os.path.join(sys.path[0], "static", "images", "articlecover", tagArticle.pictuername)
            #print(filepath)
            if os.path.exists(filepath):
                os.remove(filepath)
            self.session.delete(tagArticle)
            self.session.commit()
        #重定向回文章管理界面
        self.redirect("/system/learning")

    #post用于处理下方的多选删除请求
    @tornado.web.authenticated
    def post(self,cls):
        # 传递的是数组等多个结果的值时，一定要用get_arguments，get_argument一次只能获取一个结果
        deletetag = self.get_arguments("check_val[]")
        print(deletetag)
        #确认参数是否正确
        if cls == "all" and deletetag:
            for id in deletetag:
                tagArticle = self.session.query(Article).filter(Article.id == id).first()
                #确认文章是否存在
                if tagArticle:
                    self.session.delete(tagArticle)
            self.session.commit()
        self.write("ture")
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
    def render(self, article):
        print(article)
        articleData = {
            "month_day":article["date"].strftime("%m-%d"),
            "year":article["date"].strftime("%Y"),
            "title":article["title"],
            "image":article["pictuername"],
            "describe":article["describe"],
        }
        print(type(article["date"]))
        print(article["date"].strftime("%Y-%m-%d"))
        return self.render_string("modules\TimeLine.html",article=articleData)

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
    def render(self, category):
        return self.render_string("modules\LearnGroup.html",category=category)

class MessageModul(tornado.web.UIModule):
    def render(self, clas):
        data = {
            "target":"/index",
            "phone":"girl.jpg",
            "message":"当您驻足停留过，从此便注定我们的缘分。站在时间的尽头，我们已是朋友，前端的路上我再也不用一个人独自行走。",
        }
        return self.render_string("modules\BBSMessage.html",data=data)

class ArticleManageItemModul(tornado.web.UIModule):
    def render(self, article):
        return self.render_string("modules\ArticleManageItem.html",article=article)

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
                    "ArticleManageItem":ArticleManageItemModul,
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
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler),
    (r"/system/index", SystemIndexHandler),
    (r"/system/learning", SystemLearningHandler),
    (r"/system/article/add", SystemArticleAddPageHandler),
    (r"/system/handle/fileupload", SystemFileUploadHandler),
    (r"/system/handle/addarticle", SystemAddArticleHandler),
    (r"/system/handle/updatearticle/(\d+)", SystemUpdateArticleHandler),
    (r"/system/handle/deletearticle/(\w+)", SystemDeleteArticleHandler),
],**settings)

if __name__ == "__main__":
    #初始化数据库
    orm.Base.metadata.create_all(orm.engine)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()