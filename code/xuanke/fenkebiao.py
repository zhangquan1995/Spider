# Python35 爬虫 选课/改课MySQL
# 注：请修改login()学号密码进行爬取
# -*-encoding:utf-8-*-
# coding=utf-8
import requests
import csv
from bs4 import BeautifulSoup
import pymysql
import re


class XDspiderKeBiao:
    def __init__(self, auth_url=None, log_url=None):
        if not auth_url:
            # 登录界面 post
            self.auth_url = "http://ids.xidian.edu.cn/authserver/login?service=http%3A%2F%2Fjwxt.xidian.edu.cn%2Fcaslogin.jsp"
            self.log_url = "http://jwxt.xidian.edu.cn/caslogin.jsp"
        else:
            self.auth_url = auth_url
            self.log_url = log_url
        self.session = requests.Session()

    def login(self, id='1601120338', password='113411'):
        r = self.session.get(self.auth_url)
        data = r.text
        bsObj = BeautifulSoup(data, "html.parser")
        # 登录所需信息
        lt_value = bsObj.find(attrs={"name": "lt"})['value']
        exe_value = bsObj.find(attrs={"name": "execution"})['value']
        params = {'username': id, 'password': password,
                  "submit": "", "lt": lt_value, "execution": exe_value,
                  "_eventId": "submit", "rmShown": '1'}
        # 模拟登录报头
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
                   'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                   "Accept-Encoding": "gzip, deflate",
                   "Referer": "http://ids.xidian.edu.cn/authserver/login?service=http%3A%2F%2Fjwxt.xidian.edu.cn%2Fcaslogin.jsp",
                   "Content-Type": "application/x-www-form-urlencoded"}
        s = self.session.post(self.auth_url, data=params, headers=headers)
        s = self.session.get(self.log_url)
    # 将爬取的数据存为CSV文件

    def Store(self):
        # 改课选课
        grade_page = self.session.get(
            "http://yjsxt.xidian.edu.cn/electiveForwardAction.do")

        bsObj = BeautifulSoup(grade_page.text, "html.parser")
        table = bsObj.findAll("table", {"class": "list_2title"})[0]
        rows = table.findAll("tr")
        # 删除特定的标签和其标签下的内容
        # 方法：
        # 去除标签：[s.extract() for s in soup('script')]

        [s.extract() for s in bsObj.findAll(
            'td', attrs={'class': "special_background textLeft"})]

        csvFile = open('./xuankegaike.csv', 'w', newline='', encoding='utf-8')
        writer = csv.writer(csvFile)

        writer.writerow(('课程编号', '课程名称', '学分', '学位课', '上课学期',
                         '任课教师', '校区', '上课地点/星期/节次/周次', '分班号'))
        csvRow = []

        try:
            for row in rows:
                csvRow = []

                # for cell in row.findAll('td')[:-1]:
                for cell in row.findAll('td', attrs={'valign': "middle"})[:-1]:
                    csvRow.append(cell.get_text().strip().replace(' ', ''))
                writer.writerow(csvRow)
        finally:
            csvFile.close()

        csvFile1 = open('./xuankegaike.csv', 'r', encoding='utf-8')
        reader = csv.DictReader(csvFile1)

    # 修改小问题程序专用
    def saveMysql(self):
        csvFile1 = open('./xuankegaike.csv', 'r', encoding='utf-8')
        reader = csv.DictReader(csvFile1)

        for e in reader:
            # 是否是学位课
            if e['学位课'] == '是':
                e['学位课'] = '1'
            else:
                e['学位课'] = '0'
            # 学期
            if e['上课学期'] == '2016秋':
                e['上课学期'] = '0'
            else:
                e['上课学期'] = '1'
            # 星期
            # e['上课地点/星期/节次/周次'].replace("星期一","1")

            # e['上课地点/星期/节次/周次'].split('/')
            # 连接到数据库
            connection = pymysql.connect(host='127.0.0.1', user='root', password='root', db='test3', charset='utf8',
                                         cursorclass=pymysql.cursors.DictCursor)
            # 执行sql语句
            # strip() 去除空格
            try:
                with connection.cursor() as cursor:
                    sql = "insert into `course`(`course_id`,`course_name`,`credit`,`degree`,`term`,`teacher_name`,`campus`,`classroom`,`course_day`,`course_time`,`course_week`,`classnumber`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    # # 使用 execute()  方法执行 SQL 查询
                    try:
                        if len(e['上课地点/星期/节次/周次']) > 60:
                            cursor.execute(sql, (
                                e['课程编号'].strip(),
                                e['课程名称'].strip(),
                                e['学分'].strip(),
                                e['学位课'].strip(),
                                e['上课学期'].strip(),
                                e['任课教师'].strip(),
                                e['校区'].strip(),
                                e['上课地点/星期/节次/周次'].split("/")[0],
                                e['上课地点/星期/节次/周次'].split("/")[1],
                                e['上课地点/星期/节次/周次'].split(
                                    "(")[1].split(")")[0][0],
                                e['上课地点/星期/节次/周次'].split("/")[2][5:-
                                                                 5].lstrip(')'),
                                e['分班号'].strip()))

                        # 存两次
                            cursor.execute(sql, (
                                e['课程编号'].strip(),
                                e['课程名称'].strip(),
                                e['学分'].strip(),
                                e['学位课'].strip(),
                                e['上课学期'].strip(),
                                e['任课教师'].strip(),
                                e['校区'].strip(),
                                e['上课地点/星期/节次/周次'].split("/")[2][-5:],
                                e['上课地点/星期/节次/周次'].split("/")[3],
                                e['上课地点/星期/节次/周次'].split("/")[4][1],
                                e['上课地点/星期/节次/周次'].split(
                                    "/")[4][5:].lstrip(')'),
                                e['分班号'].strip()))

                        else:
                            cursor.execute(sql, (
                                e['课程编号'].strip(),
                                e['课程名称'].strip(),
                                e['学分'].strip(),
                                e['学位课'].strip(),
                                e['上课学期'].strip(),
                                e['任课教师'].strip(),
                                e['校区'].strip(),
                                e['上课地点/星期/节次/周次'].split("/")[0],
                                e['上课地点/星期/节次/周次'].split("/")[1],
                                e['上课地点/星期/节次/周次'].split(
                                    "(")[1].split(")")[0][0],
                                e['上课地点/星期/节次/周次'].split(
                                    "/")[2][5:].lstrip(')'),
                                e['分班号'].strip()))

                    except:
                        # else len(e['上课地点/星期/节次/周次']) == 0:
                        cursor.execute(sql, (
                            e['课程编号'].strip(),
                            e['课程名称'].strip(),
                            e['学分'].strip(),
                            e['学位课'].strip(),
                            e['上课学期'].strip(),
                            e['任课教师'].strip(),
                            e['校区'].strip(),
                            e['上课地点/星期/节次/周次'],
                            e['上课地点/星期/节次/周次'],
                            e['上课地点/星期/节次/周次'],
                            e['上课地点/星期/节次/周次'],
                            e['分班号'].strip()))

                    connection.commit()
            finally:

                connection.close()

if __name__ == '__main__':
    # 初始化爬虫对象
    XD = XDspiderKeBiao()
    # 登录(在此处传入正确的个人学号与密码信息)
    XD.login(id='1601120338', password='113411')
    XD.Store()
    XD.saveMysql()
