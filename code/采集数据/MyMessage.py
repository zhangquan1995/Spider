#Python35 爬虫 西电研究生教务处 我的消息（系统消息、成绩提示等）
#注：请修改login()学号密码进行爬取
#肖洒 2017/02/01 V1.0
# -*-encoding:utf-8-*-
# coding=utf-8
__author__ = 'ysc'
import requests
import csv
from bs4 import BeautifulSoup


class ScrapeGrade:
    def __init__(self, auth_url=None, log_url=None):
        if not auth_url:
            self.auth_url = "http://ids.xidian.edu.cn/authserver/login?service=http%3A%2F%2Fjwxt.xidian.edu.cn%2Fcaslogin.jsp"
            self.log_url = "http://jwxt.xidian.edu.cn/caslogin.jsp"
        else:
            self.auth_url = auth_url
            self.log_url = log_url
        self.session = requests.Session()

    def login(self, id='学号', password='密码'):
        r = self.session.get(self.auth_url)
        data = r.text
        bsObj = BeautifulSoup(data, "html.parser")
        lt_value = bsObj.find(attrs={"name": "lt"})['value']
        exe_value = bsObj.find(attrs={"name": "execution"})['value']
        params = {'username': id, 'password': password,
                  "submit": "", "lt": lt_value, "execution": exe_value,
                  "_eventId": "submit", "rmShown": '1'}
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
           'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
           "Accept-Encoding": "gzip, deflate",
           "Referer": "http://ids.xidian.edu.cn/authserver/login?service=http%3A%2F%2Fjwxt.xidian.edu.cn%2Fcaslogin.jsp",
           "Content-Type": "application/x-www-form-urlencoded"}
        s = self.session.post(self.auth_url, data=params, headers=headers)
        s = self.session.get(self.log_url)

    def Print(self):
        grade_page = self.session.get("http://yjsxt.xidian.edu.cn/info/findAllMessageAction.do")
        bsObj2 = BeautifulSoup(grade_page.text, "html.parser")
        nameList = bsObj2.findAll("li")
        for name in nameList:
           print(name.get_text())


if __name__ == '__main__':
    # 初始化爬虫对象
    sg = ScrapeGrade()
    # 登录(在此处传入正确的个人学号与密码信息)
    sg.login(id='学号', password='密码')
    sg.Print()