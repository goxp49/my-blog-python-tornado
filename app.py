# -*- coding: UTF-8 -*-
import json
import platform
from datetime import datetime
from sqlalchemy import func
import tornado.web
import orm
from orm import User,Article,LifeShare,BBS,System,Category,Loginlog
import os,sys,time
import hashlib                      #用于md5加密
from PIL import Image               #用于图片处理
import random                       #用于生成随机数
#----------------------------------------------------------------------------------------------------------
#-------------------------------------------- there is database --------------------------------------------
#----------------------------------------------------------------------------------------------------------
SexSelect = ["女","男"]

UserClass = ["普通用户","管理员"]

visibilitySelect = [["checked", ""],
                    ["", "checked"],
                    ]

defaultCategory = [{"id":0,"categoryname":"python","describe":"python","number":0},
                   {"id": 1, "categoryname": "JavaScript", "describe": "JavaScript", "number": 1},
                   {"id": 2, "categoryname": "Tornado", "describe": "Tornado", "number": 2},
                   {"id": 3, "categoryname": "Sqlalchemy", "describe": "Sqlalchemy", "number": 3},
                   {"id": 4, "categoryname": "第三方插件", "describe": "第三方插件", "number": 4}]
#----------------------------------------------------------------------------------------------------------
#-------------------------------------------- there is common define --------------------------------------
#----------------------------------------------------------------------------------------------------------
def ReadHtmlHeadSetting(self):
    htmlHead = {}
    htmlHead["mainTitle"] = ""
    htmlHead["subTitle"] = ""
    htmlHead["webURL"] = ""
    htmlHead["webKeywork"] = ""
    htmlHead["webDescription"] = ""
    htmlHead["webEmail"] = ""
    htmlHead["webICP"] = ""
    htmlHead["cookieTime"] = ""
    if self.session.query(System).filter(System.dataclass == "mainTitle").first():
        htmlHead["mainTitle"] = self.session.query(System).filter(System.dataclass == "mainTitle").first().content
    if self.session.query(System).filter(System.dataclass == "subTitle").first():
        htmlHead["subTitle"] = self.session.query(System).filter(System.dataclass == "subTitle").first().content
    if self.session.query(System).filter(System.dataclass == "webURL").first():
        htmlHead["webURL"] = self.session.query(System).filter(System.dataclass == "webURL").first().content
    if self.session.query(System).filter(System.dataclass == "webKeywork").first():
        htmlHead["webKeywork"] = self.session.query(System).filter(System.dataclass == "webKeywork").first().content
    if self.session.query(System).filter(System.dataclass == "webDescription").first():
        htmlHead["webDescription"] = self.session.query(System).filter(System.dataclass == "webDescription").first().content
    if self.session.query(System).filter(System.dataclass == "webEmail").first():
        htmlHead["webEmail"] = self.session.query(System).filter(System.dataclass == "webEmail").first().content
    if self.session.query(System).filter(System.dataclass == "webICP").first():
        htmlHead["webICP"] = self.session.query(System).filter(System.dataclass == "webICP").first().content
    if self.session.query(System).filter(System.dataclass == "cookieTime").first():
        htmlHead["cookieTime"] = self.session.query(System).filter(System.dataclass == "cookieTime").first().content

    return htmlHead

#----------------------------------------------------------------------------------------------------------
#-------------------------------------------- there is handler --------------------------------------------
#----------------------------------------------------------------------------------------------------------

class BaseHandle(tornado.web.RequestHandler):
    def initialize(self):
        self.session = orm.SessionType()

    def get_current_user(self):
        user = self.session.query(User).filter(User.name == self.get_secure_cookie("username")).first()
        print(self.get_secure_cookie("username"))
        if user:
            self.currentuser = self.get_secure_cookie("username")
            self.user = self.session.query(User).filter(User.name == self.currentuser).first()
            #print("BaseHandle："+self.user.name)
            return True
        print("认证失败")
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
        htmlHead = ReadHtmlHeadSetting(self)
        self.render("index.html",TitleNum = range(3),Articles = allArticles,htmlHead=htmlHead)

class AboutHandler(BaseHandle):
    def get(self):
        tarData = self.session.query(System).filter(System.dataclass == "introduce").first()
        if tarData:
            introduce = tarData.content
        else:
            introduce = "这家伙很懒，个人简介都没写！"
        htmlHead = ReadHtmlHeadSetting(self)

        self.render("about.html",ItemNum = ["n1","n2","n3","n4","n5"],introduce = introduce,htmlHead=htmlHead)

class LifeHandler(BaseHandle):
    def get(self):
        allShares = []
        lifeshares = self.session.query(LifeShare).all()
        for lifeshare in lifeshares:
            tempList = {}
            tempList["id"] = lifeshare.id
            tempList["title"] = lifeshare.title
            tempList["describe"] = lifeshare.describe
            tempList["pictuername"] = lifeshare.pictuername
            allShares.append(tempList)
        htmlHead = ReadHtmlHeadSetting(self)
        self.render("slowlife.html",ShareNum = allShares,htmlHead=htmlHead)

class LearnHandler(BaseHandle):
    def get(self,clas):
        #根据clas分类显示不同类型的文章
        allArticles = []
        allCategory = []
        allCategoryDataBase = self.session.query(Category).all()
        #提取所有数据,用于顶部标签显示
        for categoryDataBase in allCategoryDataBase:
            tempDict = {}
            tempDict["id"] = categoryDataBase.id
            tempDict["categoryname"] = categoryDataBase.categoryname
            allCategory.append(tempDict)

        if(clas=="all"):
            articles = self.session.query(Article).all()
        else:
            articles = self.session.query(Article).filter(Article.category == clas).all()
        #确定是否有找到对象
        if articles:
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
        htmlHead = ReadHtmlHeadSetting(self)
        self.render("learn.html",categories = allCategory,Articles = allArticles,htmlHead=htmlHead)

class BBSHandler(BaseHandle):
    def get(self):
        allMessages = []
        mssages = self.session.query(BBS).all()
        for message in mssages:
            tempList = {}
            tempList["id"] = message.id
            tempList["content"] = message.content
            tempList["date"] = message.date
            #点击头像后跳转的连接，还没实现
            tempList["target"] = "/bbs"
            # 头像图片，还没实现
            tempList["icon"] = "ico_%d.jpg" % (message.icon)    #"ico_1.jpg"
            allMessages.append(tempList)
        htmlHead = ReadHtmlHeadSetting(self)
        self.render("bbs.html",allMessages = allMessages,htmlHead=htmlHead)


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
        #print("Ajax Post:" + username + "密码为:" + password)
        result = self.session.query(User).filter(User.name == username,User.password == password).first()
        #如果用户存在，则返回User对象
        if result:
            data['status'] = True
            data["message"] = "successfully"
            data["url"] = "/system/index"
            #2018.6.1增加从数据库中读取Cookie有效期
            cookieTime = self.session.query(System).filter(System.dataclass == "cookieTime").first()
            if cookieTime:
                self.set_secure_cookie("username", result.name,expires=time.time()+int(cookieTime.content)*60*60) #单位是秒，要加上时区
            else:
                self.set_secure_cookie("username", result.name,expires_days=1) #这里设置有效期默认为1天
            #登陆次数+1
            result.loginnum = result.loginnum + 1
            #更新最后一次登录时间
            result.lasttime = result.curtime
            result.curtime = datetime.now()
            # 更新最后一次登录IP
            result.lastip = result.curip
            result.curip = self.request.remote_ip
            print("当前登录用户为：" + result.name + "    密码：" + result.password)
            #***********************2018.5.31 增加登录记录数据库表存储每次登录数据********************
            self.session.add(Loginlog(username=result.name, ipaddress=self.request.remote_ip,date=datetime.now()))
            self.session.commit()
        #将data序列化为JSON回传给前端
        self.write(json.dumps(data))

class LogoutHandler(BaseHandle):
    def get(self):
        self.clear_cookie("username")
        #self.set_secure_cookie("username", None)
        # 重定向回文章管理界面
        self.redirect("/index")

class RegisterHandler(BaseHandle):
    def get(self):
        self.render("register.html")

    def post(self):
        data = {'status': False, 'message': '信息填写错误，请重新输入！', 'url': "/login"}  # 封装数据
        target = self.get_argument("target", None)
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        mobile = self.get_argument("mobile", None)
        email = self.get_argument("email", None)
        sex = True if self.get_argument("sex", False) == "true" else False
        admin = True if self.get_argument("admin", False) == "true" else False
        print(username)
        print(password)
        print(mobile)
        print(email)
        print(sex)
        print(admin)
        userNameCheck = self.session.query(User).filter(User.name == username).first()
        #先处理单独项目Ajax提交
        #如果需要查询username，则判断数据库中是否已存在
        if target == "username":
            if userNameCheck:
                self.write("false")
            else:
                self.write("true")
            return self.finish()  # 如果不加这一段，还会执行下面的语句，类似break
        elif not target and not userNameCheck and username and password and email:
            self.session.add(User(name=username, password=password, mail=email, regdate=datetime.now(),mobile=mobile,
                                  admin=admin,sex=sex))
            self.session.commit()
            #更新传递给前端的信息
            data['status'] = True
            data['message'] = "注册成功，请您重新登录，正在为您跳转…………"
            self.write(json.dumps(data))

class ViewHandler(BaseHandle):
    def get(self,obj,id):
        #通过obj判断要查看什么内容
        if(obj == "lifeshare"):
            lifeshare = self.session.query(LifeShare).filter(LifeShare.id == id).first()
            #判断文章是否存在
            if lifeshare:
                title = lifeshare.title
                content = lifeshare.content
                date = lifeshare.date
                username = lifeshare.userName
                viewNum = 0
            htmlHead = ReadHtmlHeadSetting(self)
            self.render("view-lifeshare.html",title=title,content=content,date=date,username=username,viewNum=viewNum,
                        htmlHead=htmlHead)

        elif (obj == "learn"):
            article = self.session.query(Article).filter(Article.id == id).first()
            # 判断文章是否存在
            if article:
                title = article.title
                content = article.content
                date = article.date
                username = article.userName
                viewNum = 0
            htmlHead = ReadHtmlHeadSetting(self)
            self.render("view-learn.html", title=title, content=content, date=date, username=username,
                        viewNum=viewNum,htmlHead=htmlHead)

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
        article_num = self.session.query(Article).count()
        messageNumber = self.session.query(BBS).count()
        self.render("backstage\index.html",current_user = self.currentuser,login_num = self.user.loginnum,mail = self.user.mail,
                    phone = self.user.mobile,last_time = self.user.lasttime,last_ip = self.user.lastip,admin_num = admin_num,
                    browser = browser,python_version = platform.python_version(),os = windows,member_num = member_num,
                    current_ip = current_ip,time = time,articleNumber=article_num,messageNumber=messageNumber)


class SystemLearningHandler(BaseHandle):

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
            # 增加从数据库获取文章分类 by 2018.5.26
            tempList["category"] = self.session.query(Category).filter(Category.id == article.category).first().categoryname
            tempList["keywork"] = article.keywork
            # 留言数还没实现，先用0表示
            tempList["msg"] = 0
            tempList["date"] = article.date
            allArticles.append(tempList)
        self.render(r"backstage\learning.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                    articlesNum = articlesNum,articles = allArticles)

class SystemLifeShareHandler(BaseHandle):

    @tornado.web.authenticated
    def get(self):
        allShare = []
        #如果当前用户为管理员，则显示所有人的文章
        if(self.session.query(User).filter(User.name == self.currentuser,User.admin == True).first()):
            print("当前是管理员，显示所有文章")
            articles = self.session.query(LifeShare).all()
            #获得文章数量
            shareNum = len(articles)
        else:
            print("当前是普通用户，只显示个人文章")
            articles = self.session.query(LifeShare).filter(LifeShare.userName == self.currentuser).all()
            # 获得文章数量
            shareNum = len(articles)
        for article in articles:
            tempList = {}
            tempList["id"] = article.id
            tempList["title"] = article.title
            tempList["date"] = article.date
            allShare.append(tempList)
        self.render(r"backstage\lifeshare.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                    shareNum = shareNum,shares = allShare)

class SystemMessageHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        allMessage = []
        messageNum = 0
        #如果当前用户为管理员，则显示所有人的留言，否则无法查看
        if(self.session.query(User).filter(User.name == self.currentuser,User.admin == True).first()):
            print("当前是管理员，显示所有文章")
            messages = self.session.query(BBS).all()
            #获得文章数量
            messageNum = len(messages)

            for message in messages:
                tempList = {}
                tempList["id"] = message.id
                tempList["content"] = message.content[0:50] #截取内容显示
                tempList["date"] = message.date
                tempList["ipaddress"] = message.ipaddress
                allMessage.append(tempList)

        self.render(r"backstage\message.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                    messageNum = messageNum,allMessage = allMessage)

class SystemAboutHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        #如果当前用户为管理员，则显示所有人的留言，否则无法查看
        if(self.session.query(User).filter(User.name == self.currentuser,User.admin == True).first()):
            systemData = self.session.query(System).filter(System.dataclass == "introduce").first()
            #如果还没设置个人介绍，则使用默认信息
            if systemData:
                introduce = systemData.content
            else:
                introduce = "这个人很懒，还没写自我介绍哦~"
            self.render(r"backstage\about.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                        introduce = introduce)

class SystemCategoryHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        #如果当前用户为管理员，则显示所有人的留言，否则无法查看
        if(self.session.query(User).filter(User.name == self.currentuser,User.admin == True).first()):
            categores = self.session.query(Category).all()
            #如果没存储过分类数据，则使用默认分组存入数据库
            allCategory = []
            if categores:
                for category in categores:
                    tempDict = {}
                    tempDict["id"] = category.id
                    tempDict["categoryname"] = category.categoryname
                    tempDict["describe"] = category.describe
                    #分类文章量直接从Article数据库查询
                    tempDict["number"] = self.session.query(Article).filter(Article.category == category.id).count()
                    allCategory.append(tempDict)
            else:
                for defualtData in defaultCategory:
                    categoryDataBase = Category()
                    categoryDataBase.id = defualtData["id"]
                    categoryDataBase.categoryname = defualtData["categoryname"]
                    categoryDataBase.describe = defualtData["describe"]
                    categoryDataBase.number = defualtData["number"]
                    self.session.add(categoryDataBase)
                self.session.commit()
                allCategory = defaultCategory
            self.render(r"backstage\category.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                        categoryItem = allCategory)

class SystemManageUserHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        #当前用户为管理员，否则无法查看
        if(self.session.query(User).filter(User.name == self.currentuser,User.admin == True).first()):
            allUserDase = self.session.query(User).all()
            userNumber = 0
            allUser = []
            for user in allUserDase:
                userNumber += 1
                tempDict = {}
                tempDict["id"] = user.id
                tempDict["name"] = user.name
                tempDict["sex"] = SexSelect[user.sex]
                tempDict["regdate"] = user.regdate
                tempDict["curtime"] = user.curtime
                tempDict["admin"] = UserClass[user.admin]
                allUser.append(tempDict)

            self.render(r"backstage\manage-user.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                        userItem = allUser,userNumber=userNumber)

class SystemLoginlogHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        #当前用户为管理员，否则无法查看
        if(self.session.query(User).filter(User.name == self.currentuser,User.admin == True).first()):
            allLogDataBase = self.session.query(Loginlog).all()
            logNumber = 0
            allLog = []
            for loginlog in allLogDataBase:
                tempDict = {}
                logNumber += 1
                tempDict["id"] = loginlog.id
                tempDict["username"] = loginlog.username
                tempDict["ipaddress"] = loginlog.ipaddress
                tempDict["date"] = loginlog.date
                allLog.append(tempDict)

            self.render(r"backstage\loginlog.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                        logItem = allLog,logNumber=logNumber)

class SystemSettingHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self,cls):
        htmlHead = ReadHtmlHeadSetting(self)
        self.render(r"backstage\base-setting.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                    htmlHead = htmlHead)


class SystemArticleAddPageHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        allCategory = []
        allCategoryDataBase = self.session.query(Category).all()
        #提取所有数据,用于顶部标签显示
        for categoryDataBase in allCategoryDataBase:
            tempDict = {}
            tempDict["id"] = categoryDataBase.id
            tempDict["categoryname"] = categoryDataBase.categoryname
            tempDict["check"] = "checked"
            allCategory.append(tempDict)

        self.render(r"backstage\add-article.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                    article_status = "未发表",article_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),categoryItem=allCategory
                    )

class SystemLifeShareAddPageHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        self.render(r"backstage\add-lifeshare.html",current_user = self.currentuser,mail = self.user.mail,phone = self.user.mobile,
                    share_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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

class SystemAddLifeShareHandler(BaseHandle):
    @tornado.web.authenticated
    def post(self):
        title = self.get_argument("title")
        content = self.get_argument("content")
        describe = self.get_argument("describe")
        visibility = self.get_argument("visibility")
        pictuerName = self.get_argument("pictuername")
        #print(title + "------" + content + "------" + describe + "------" + category + "------" + keywork + "------" + password + "------" + visibility + "------" + pictuerName)
        #将文章内容存储到数据库中
        self.session.add(LifeShare(userName = self.user.name,title = title,content = content,describe = describe,
                                 visibility = visibility,pictuername = pictuerName,date = datetime.now()))
        self.session.commit()
        data = {'message': '文章已发表成功！', 'url': "/system/lifeshare"}  # 封装数据
        #回传AJAX结果
        self.write(json.dumps(data))

class SystemAddBBSMssageHandler(BaseHandle):
    def post(self):
        #由于CSS问题，此处要将wangeditor自动生成的<p>标签删除，否则会显示异常
        content = self.get_argument("content").replace('<p>','').replace('</p>','')
        #将文章内容存储到数据库中
        self.session.add(BBS(ipaddress=self.request.remote_ip,content = content,date = datetime.now(),
                             icon=random.randint(1,20)))
        self.session.commit()
        data = {'message': '留言已发表成功！', 'url': "/bbs"}  # 封装数据
        #回传AJAX结果
        self.write(json.dumps(data))

class SystemAddCategoryHandler(BaseHandle):
    @tornado.web.authenticated
    def post(self):
        data = {'message': '栏目分类已添加成功！', 'status': "success"}  # 封装数据
        id = self.get_argument("id",None)
        categoryname = self.get_argument("categoryname",None)
        describe = self.get_argument("describe",None)
        #检查id与栏目名是否合法
        if id and categoryname :
            #如果ID已存在则提示
            if self.session.query(Category).filter(Category.id == id).first():
                data["message"]="该ID已存在，请重新填写！"
                data["status"]="fail"
                self.write(json.dumps(data))
                self.flush()
                return
            # 如果栏目名称已存在则提示
            elif self.session.query(Category).filter(Category.categoryname == categoryname).first():
                data["message"] = "该栏目名称已存在，请重新填写！"
                data["status"] = "fail"
                self.write(json.dumps(data))
                self.flush()
                return
            else:
                self.session.add(Category(id=id, categoryname=categoryname, describe=describe))
                self.session.commit()
        #回传AJAX结果
        self.write(json.dumps(data))

class SystemFileUploadHandler(BaseHandle):

    @tornado.web.authenticated
    def post(self,handler):
        #如果是上传封面图片
        if(handler == "cover"):
            #这里的属性名要和html中的name一样
            FileData =  self.request.files["input-file"]
            for file in FileData:
                #print(file)
                #filetype = file["content_type"]
                #filename = file["filename"]
                filebody = file["body"]
                filehash = hashlib.md5(filebody).hexdigest()
                #print(hashlib.md5((self.user.name + datetime.now().strftime("%Y%m%d%H%M%S") + filehash).encode('utf-8')).hexdigest())
                #获得发送来的文件后缀名
                filesuffix = os.path.splitext(file["filename"])[1]
                #设置存储图片路径,文件命名方式：用户名 + 日期 + hash值
                filename = hashlib.md5((self.user.name + datetime.now().strftime("%Y%m%d%H%M%S") + filehash).encode('utf-8')).hexdigest() + filesuffix
                filepath = os.path.join(sys.path[0],"static","images","articlecover",filename)
                #print(filepath)
                with open(filepath, 'wb') as f:
                    f.write(filebody)
                try:
                    image = Image.open(filepath)
                    newimage = image.resize((300, 256), Image.ANTIALIAS)
                   #newimage.show()
                    newimage.save(filepath)
                except IOError:
                    print("cannot create thumbnail for", filepath)

                #将保存的文件名回传回去(JSON格式)
                self.write({"msg":"文章发布成功！","pictuer":filename})

        #如果是上传编辑器中的图片
        if(handler == "editorpicture"):
            #这里的属性名要和editor.customConfig.uploadFileName一样！
            PictureData =  self.request.files["EditorPicture"]
            for picture in PictureData:
                print(picture)
                filebody = picture["body"]
                filehash = hashlib.md5(filebody).hexdigest()
                #获得发送来的文件后缀名
                filesuffix = os.path.splitext(picture["filename"])[1]
                #设置存储图片路径,文件命名方式：用户名 + 日期 + hash值
                filename = hashlib.md5((self.user.name + datetime.now().strftime("%Y%m%d%H%M%S") + filehash).encode('utf-8')).hexdigest() + filesuffix
                filepath = os.path.join(sys.path[0],"static","images","editorpicture",filename)
                #print(filepath)
                with open(filepath, 'wb') as f:
                    f.write(filebody)
                #注意：此处路径static前有"/"表示使用的是绝对路径
                resultDate={
                    "errno": 0,
                    "data": [
                        "/static/images/editorpicture/"+filename,
                        ]
                }

            #将保存的文件名回传回去(JSON格式)
            self.write(resultDate)



class SystemUpdateHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self,obj,id):
        #判断是否要修改学习文章
        if obj == "article":
            tagArticle = self.session.query(Article).filter(Article.id == id).first()
            #确定存在该id的文章
            if tagArticle:
                title = tagArticle.title
                content = tagArticle.content
                describe = tagArticle.describe
                keywork = tagArticle.keywork
                passwork = tagArticle.password
                visibility = visibilitySelect[tagArticle.visibility]
                date = tagArticle.date

                # 获取栏目分类 by 2018.5.27
                allCategory = []
                allCategoryDataBase = self.session.query(Category).all()
                # 提取所有数据,用于顶部标签显示
                for categoryDataBase in allCategoryDataBase:
                    tempDict = {}
                    tempDict["id"] = categoryDataBase.id
                    tempDict["categoryname"] = categoryDataBase.categoryname
                    if tagArticle.category == categoryDataBase.id:
                        tempDict["check"] = "checked"
                    else:
                        tempDict["check"] = ""
                    allCategory.append(tempDict)

                self.render(r"backstage\update-article.html",article_title = title,article_content = content,
                            article_describe = describe,article_keywork = keywork,categoryItem=allCategory,
                            article_passwork = passwork,article_visibility = visibility,article_date = date,
                            article_id = id,
                            current_user=self.currentuser, mail=self.user.mail, phone=self.user.mobile,
                            )
        # 判断是否要修改生活分享
        elif obj == "lifeshare":
            tagShare = self.session.query(LifeShare).filter(LifeShare.id == id).first()
            # 确定存在该id的文章
            if tagShare:
                title = tagShare.title
                content = tagShare.content
                describe = tagShare.describe
                visibility = visibilitySelect[tagShare.visibility]
                date = tagShare.date
                inipictureaddress = tagShare.pictuername
                self.render(r"backstage\update-lifeshare.html", share_title=title, share_content=content,
                            share_describe=describe,share_visibility=visibility, share_date=date,
                            share_id=id,inipictureaddress=inipictureaddress,
                            current_user=self.currentuser, mail=self.user.mail, phone=self.user.mobile,
                            )
        # 判断是否要修改生活分享
        elif obj == "category":
            tagCategory = self.session.query(Category).filter(Category.id == id).first()
            # 确定存在该id的文章
            if tagCategory:
                id = tagCategory.id
                categoryname = tagCategory.categoryname
                describe = tagCategory.describe

                self.render(r"backstage\update-category.html", current_user=self.currentuser, mail=self.user.mail,
                            phone=self.user.mobile,id =id,categoryname=categoryname,describe=describe
                            )

    @tornado.web.authenticated
    def post(self,obj, id):
        # 判断是否要修改学习文章
        if obj == "article":
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
        # 判断是否要修改生活分享
        elif obj == "lifeshare":
            tagArticle = self.session.query(LifeShare).filter(LifeShare.id == id).first()
            # 确定存在该id的文章
            if tagArticle:
                #如果有replace，代表有上传新的封面，需要把旧的图片删除
                if(self.get_argument("replace",None)) :
                    filepath = os.path.join(sys.path[0], "static", "images", "articlecover", tagArticle.pictuername)
                    #先判断文件是否存在才删除
                    if(os.path.exists(filepath)):
                        os.remove(filepath)
                    #更新图片名称
                    tagArticle.pictuername = self.get_argument("pictuername", None)
                tagArticle.title = self.get_argument("title",None)
                tagArticle.content = self.get_argument("content",None)
                tagArticle.describe = self.get_argument("describe",None)
                tagArticle.visibility = self.get_argument("visibility",None)
                tagArticle.date = datetime.now()
                #将文章内容更新到数据库中
                self.session.commit()
                data = {'message': '生活分享已更新成功！', 'url': "/system/lifeshare"}  # 封装数据
                #回传AJAX结果
                self.write(json.dumps(data))

        # 判断是否要修改栏目分类
        elif obj == "category":
            data = {'message': '栏目分类已修改成功！', 'status': "success"}  # 封装数据
            #注意，这里的newid是要修改成的新id，id是原本的id
            newid = self.get_argument("newid", None)
            categoryname = self.get_argument("categoryname", None)
            describe = self.get_argument("describe", None)
            oldcategoryname = self.get_argument("oldcategoryname", None)
            # 检查id与栏目名是否合法
            if newid and categoryname:
                # 如果ID已存在,且不等于原id
                if self.session.query(Category).filter(Category.id == newid).first() and newid != id:
                    data["message"] = "该ID已存在，请重新填写！"
                    data["status"] = "fail"
                    self.write(json.dumps(data))
                    self.flush()
                    return
                # 如果栏目名称已存在则提示
                elif self.session.query(Category).filter(Category.categoryname == categoryname).first() and oldcategoryname != categoryname:
                    data["message"] = "该栏目名称已存在，请重新填写！"
                    data["status"] = "fail"
                    self.write(json.dumps(data))
                    self.flush()
                    return
                else:
                    tarcategory = self.session.query(Category).filter(Category.id == newid).first()
                    tarcategory.id = newid
                    tarcategory.categoryname = categoryname
                    tarcategory.describe = describe
                    self.session.commit()
                    # 回传AJAX结果
                    self.write(json.dumps(data))
        # 判断是否要修改栏目分类
        elif obj == "user":
            data = {'message': '用户信息已修改成功！', 'status': "success"}  # 封装数据
            mail = self.get_argument("mail", None)
            mobile = self.get_argument("mobile", None)
            sex = SexSelect.index(self.get_argument("sex", None))
            admin = UserClass.index(self.get_argument("admin", None))
            password = self.get_argument("admin", None)
            tarUser = self.session.query(User).filter(User.id == id).first()
            if tarUser:
                tarUser.mail = mail
                tarUser.mobile = mobile
                tarUser.sex = sex
                tarUser.admin = admin
                tarUser.password = password
                self.session.commit()
            else:
                data = {'message': '用户不存在！', 'status': "false"}  # 封装数据
            self.write(json.dumps(data))
        # 判断是否要修改系统设置
        elif obj == "setting":
            requestData = self.request.body_arguments
            for dataclass in requestData:
                content = self.get_argument(dataclass, "")
                #判断是否已经存在该设置内容
                tarDataBase = self.session.query(System).filter(System.dataclass == dataclass).first()
                if tarDataBase:
                    tarDataBase.handlers = self.user.name
                    tarDataBase.ipaddress = self.request.remote_ip
                    tarDataBase.dataclass = dataclass
                    tarDataBase.content = content
                    tarDataBase.date = datetime.now()
                else:
                    self.session.add(System(handlers=self.user.name, ipaddress=self.request.remote_ip, dataclass=dataclass, content=content,
                                            date=datetime.now()))
                self.session.commit()
            self.redirect("/system/setting/base")
        #如果都不是前面的，就是通过AJAX修改系统信息
        else:
            #print(self.request.body_arguments)
            #print(self.get_body_argument('dataclass'))
            tarData = self.session.query(System).filter(System.dataclass == self.get_body_argument("dataclass")).first()
            # 如果已经存在数据则直接修改
            if tarData:
                tarData.handlers = self.user.name
                tarData.ipaddress = self.request.remote_ip
                tarData.content = self.get_body_argument("content")
                tarData.date = datetime.now()
            #如果没有写入过该数据则进行添加
            else:
                self.session.add(System(handlers=self.user.name, ipaddress=self.request.remote_ip, dataclass=self.get_body_argument("dataclass"),
                           content=self.get_body_argument("content"), date=datetime.now()))

            data = {'message': '个人简介已更新成功！', 'url': "/system/about"}  # 封装数据
            self.session.commit()
            # 回传AJAX结果
            self.write(json.dumps(data))

class SystemDeleteHandler(BaseHandle):
    #get用于处理单个删除请求
    @tornado.web.authenticated
    def get(self,obj,cls):
        #判断要删除哪个表
        if(obj == "article"):
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
        elif(obj == "lifeshare"):
            tagArticle = self.session.query(LifeShare).filter(LifeShare.id == cls).first()
            # 确定存在该id的文章
            if tagArticle:
                # 先删除图片再删除数据
                filepath = os.path.join(sys.path[0], "static", "images", "articlecover", tagArticle.pictuername)
                # print(filepath)
                if os.path.exists(filepath):
                    os.remove(filepath)
                self.session.delete(tagArticle)
                self.session.commit()
            # 重定向回文章管理界面
            self.redirect("/system/lifeshare")
        elif (obj == "message"):
            tagArticle = self.session.query(BBS).filter(BBS.id == cls).first()
            # 确定存在该id的文章
            if tagArticle:
                self.session.delete(tagArticle)
                self.session.commit()
            # 重定向回文章管理界面
            self.redirect("/system/message")
        elif (obj == "category"):
            # 确认参数是否正确
            tagCategory = self.session.query(Category).filter(Category.id == cls).first()
            #先删除该分类下的文章，再删除分类
            allArticleDase = self.session.query(Article).filter(Article.category == tagCategory.id).all()
            for article in allArticleDase:
                self.session.delete(article)
            if tagCategory:
                self.session.delete(tagCategory)
            self.session.commit()
            self.redirect("/system/category")
        elif (obj == "manageuser"):
            # 确认参数是否正确
            tagUser = self.session.query(User).filter(User.id == cls).first()
            if tagUser:
                self.session.delete(tagUser)
                self.session.commit()
            self.redirect("/system/manageuser")
        elif (obj == "loginlog"):
            #判断是单个删除还是全部删除
            if cls == "all":
                if self.session.query(Loginlog):
                    self.session.query(Loginlog).delete()
            else:
                tarLoginlog = self.session.query(Loginlog).filter(Loginlog.id == cls).first()
                if tarLoginlog:
                    self.session.delete(tarLoginlog)
            self.session.commit()
            self.redirect("/system/loginlog")

    #post用于处理下方的多选删除请求
    @tornado.web.authenticated
    def post(self,obj,cls):
        if(obj=="article"):
            # 传递的是数组等多个结果的值时，一定要用get_arguments，get_argument一次只能获取一个结果
            deletetag = self.get_arguments("check_val[]")
            #确认参数是否正确
            if cls == "all" and deletetag:
                for id in deletetag:
                    tagArticle = self.session.query(Article).filter(Article.id == id).first()
                    #确认文章是否存在
                    if tagArticle:
                        self.session.delete(tagArticle)
                self.session.commit()
        if(obj=="lifeshare"):
            deletetag = self.get_arguments("check_val[]")
            # 确认参数是否正确
            if cls == "all" and deletetag:
                for id in deletetag:
                    tagArticle = self.session.query(LifeShare).filter(LifeShare.id == id).first()
                    # 确认文章是否存在
                    if tagArticle:
                        self.session.delete(tagArticle)
                self.session.commit()
        if (obj == "message"):
            deletetag = self.get_arguments("check_val[]")
            # 确认参数是否正确
            if cls == "all" and deletetag:
                for id in deletetag:
                    tagArticle = self.session.query(BBS).filter(BBS.id == id).first()
                    # 确认文章是否存在
                    if tagArticle:
                        self.session.delete(tagArticle)
                self.session.commit()

        self.write("ture")


class SystemQueryHandler(BaseHandle):
    #get用于处理单个删除请求
    @tornado.web.authenticated
    def post(self, obj, tag):
        if obj == "user":
            queryTar = self.get_argument(tag)
            tarUser = self.session.query(User).filter(User.id == queryTar).first()
            userData = {}
            userData["status"] = False
            if tarUser:
                userData["status"] = True
                userData["id"] = tarUser.id
                userData["name"] = tarUser.name
                userData["mail"] = tarUser.mail
                userData["sex"] = SexSelect[tarUser.sex]
                userData["mobile"] = tarUser.mobile
                userData["admin"] = UserClass[tarUser.admin]
            self.write(json.dumps(userData))

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
        articleData = {
            "id":article["id"],
            "month_day":article["date"].strftime("%m-%d"),
            "year":article["date"].strftime("%Y"),
            "title":article["title"],
            "image":article["pictuername"],
            "describe":article["describe"],
        }
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
    def render(self, lifeshare):
        return self.render_string("modules\SlowLifePhone.html",lifeshare=lifeshare)

class LearnGroupModul(tornado.web.UIModule):
    def render(self, category):
        return self.render_string("modules\LearnGroup.html",category=category)

class MessageModul(tornado.web.UIModule):
    def render(self, mssage):
        return self.render_string("modules\BBSMessage.html",message=mssage)

class ArticleManageItemModul(tornado.web.UIModule):
    def render(self, article):
        return self.render_string("modules\ArticleManageItem.html",article=article)

class LifeShareManageItemModul(tornado.web.UIModule):
    def render(self, share):
        return self.render_string("modules\LifeShareManageItem.html",share=share)

class MessageManageItemModul(tornado.web.UIModule):
    def render(self, message):
        return self.render_string("modules\MessageManageItem.html",message=message)

class CommonItemModul(tornado.web.UIModule):
    def render(self,moduleClass, data):
        if moduleClass == "category":
            return self.render_string("modules\CategoryManageItem.html",category=data)
        elif moduleClass == "addArticleCategory":
            return self.render_string("modules\AddArticleCategoryItem.html",category=data)
        elif moduleClass == "UserMange":
            return self.render_string(r"modules\UserManageItem.html",user=data)
        elif moduleClass == "Logoinlog":
            return self.render_string(r"modules\LoginLogItem.html",loginlog=data)

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
                    "LifeShareManageItem":LifeShareManageItemModul,
                    "MessageManageItem":MessageManageItemModul,
                    "CommonItem":CommonItemModul,
                   },
    "login_url":"/login",
    "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
    "debug":True,
}

application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/about", AboutHandler),
    (r"/slowlife", LifeHandler),
    (r"/learn/(\w+)", LearnHandler),
    (r"/bbs", BBSHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler),
    (r"/view/(\w+)/(\d+)", ViewHandler),
    (r"/system/index", SystemIndexHandler),
    (r"/system/learning", SystemLearningHandler),
    (r"/system/lifeshare", SystemLifeShareHandler),
    (r"/system/message", SystemMessageHandler),
    (r"/system/about", SystemAboutHandler),
    (r"/system/category", SystemCategoryHandler),
    (r"/system/manageuser", SystemManageUserHandler),
    (r"/system/loginlog", SystemLoginlogHandler),
    (r"/system/setting/(\w+)", SystemSettingHandler),
    (r"/system/article/add", SystemArticleAddPageHandler),
    (r"/system/lifeshare/add", SystemLifeShareAddPageHandler),
    (r"/system/handle/upload/(\w+)", SystemFileUploadHandler),
    (r"/system/handle/addarticle", SystemAddArticleHandler),
    (r"/system/handle/addlifeshare", SystemAddLifeShareHandler),
    (r"/system/handle/addbbsmssage", SystemAddBBSMssageHandler),
    (r"/system/handle/addcategory", SystemAddCategoryHandler),
    (r"/system/handle/update/(\w+)/(\d+)", SystemUpdateHandler),
    (r"/system/handle/delete/(\w+)/(\w+)", SystemDeleteHandler),
    (r"/system/handle/query/(\w+)/(\w+)", SystemQueryHandler),
],**settings)


def MainIni():
    #先将表格初始化
    session = orm.SessionType()
    checkCategory = session.query(Category).all()
    if not checkCategory:
        for defualtData in defaultCategory:
            categoryDataBase = Category()
            categoryDataBase.id = defualtData["id"]
            categoryDataBase.categoryname = defualtData["categoryname"]
            categoryDataBase.describe = defualtData["describe"]
            categoryDataBase.number = defualtData["number"]
            session.add(categoryDataBase)
        session.commit()
    session.close()




if __name__ == "__main__":
    #初始化数据库
    orm.Base.metadata.create_all(orm.engine)
    application.listen(8888)
    MainIni()
    tornado.ioloop.IOLoop.instance().start()
