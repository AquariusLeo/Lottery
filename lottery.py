import tornado.ioloop
import tornado.web
import numpy
import os.path

#全局变量初始化
list=numpy.empty(100)   #待抽取名单
total_num=0    #参与总人数
first_num=0    #一等奖剩余人数
second_num=0   #二等奖剩余人数
third_num=0    #三等奖剩余人数

#/路径处理程序
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html",flag=0)

#/list路径处理程序
class ListHandler(tornado.web.RequestHandler):
    def post(self):
        #内部作用域修改全局变量
        global list
        global total_num
        global first_num
        global second_num
        global third_num
        strName=self.get_argument("namelist")    #获取名单字符串
        list=numpy.asarray(strName.split('\r\n'))    #按行分割并存入ndarray数组
        list=numpy.unique(list)    #去重
        index=numpy.where(list == "")
        list=numpy.delete(list,index)    #去除空行
        total_num=list.size
        first_num=int(self.get_argument("firstnum"))
        second_num=int(self.get_argument("secondnum"))
        third_num=int(self.get_argument("thirdnum"))
        if first_num + second_num + third_num > total_num:
            self.render("index.html",flag=1)  #如果奖项总人数超出参与人数，重新渲染网页，传递一个参数flag给网页，网页显示一个提示框
        else:
            self.redirect("/lottery")    #重定向至/lottery

#/lottery路径处理程序
class LotteryHandler(tornado.web.RequestHandler):
    def get(self):
        #用Tornado模板渲染lottery.html
        self.render("lottery.html",flag=False,totalnum=total_num,remainnum=list.size,firstnum=first_num,secondnum=second_num,thirdnum=third_num)
    
    def post(self):
        #内部作用域修改全局变量
        global list
        global total_num
        global first_num
        global second_num
        global third_num
        price=self.get_argument("price")
        number=int(self.get_argument("num"))
        #相应奖项剩余人数减少
        if price=="first":
            first_num-=number
        elif price=="second":
            second_num-=number
        elif price=="third":
            third_num-=number

        #用numpy.random.choice从list中抽取
        winner_list=numpy.random.choice(list,number,replace=False)
        #删除已中奖人员
        for i in numpy.nditer(winner_list):
            index=numpy.where(list == i)
            list=numpy.delete(list,index)
        #再次渲染lottery.html，并显示中奖者名单
        self.render("lottery.html",flag=True,winnerlist=winner_list,totalnum=total_num,remainnum=list.size,firstnum=first_num,secondnum=second_num,thirdnum=third_num)

handlers=[
    (r"/",IndexHandler),
    (r"/list",ListHandler),
    (r"/lottery",LotteryHandler)
]

if __name__=="__main__":
    app=tornado.web.Application(handlers,static_path=os.path.join(os.path.dirname(__file__),"static"),debug=True)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()