#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import re
import getpass
from datetime import timedelta, datetime
from icalendar import Calendar, Event, Alarm
from bs4 import BeautifulSoup, SoupStrainer
from uuid import uuid1
from helpers import chinese_weekdays, unify_brackets
from urllib import quote, unquote
from EasyLogin import EasyLogin
from data import *

class _Misc(object):
    pass
_misc = _Misc()


class LoginError(Exception):
    """raise LoginError if error occurs in login process.
    """
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'LoginError: '+self.error


class GrabError(Exception):
    """raise GrabError if error occurs in grab process.
    """
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'GrabError: {}'.format(self.error)


class TeapotParser():
    """Parser for Zhejiang University.
    """
    def __init__(self):
        self.url_prefix = "http://jwbinfosys.zju.edu.cn/"
        self.charset = "gbk"

    def get_semester_from_time(self, time_text):
        if u"秋冬" in time_text:
            return u"秋冬"
        elif u"秋" in time_text:
            return u"秋"
        elif u"冬" in time_text:
            return u"冬"
        elif u"春夏" in time_text:
            return u"春夏"
        elif u"春" in time_text:
            return u"春"
        elif u"夏" in time_text:
            return u"夏"
        else:
            return None

    @staticmethod
    def parse_odd_or_even(text):
        if u"单" in text:
            return "odd"
        elif u"双" in text:
            return "even"
        else:
            return "all"

    @staticmethod
    def trim_location(l):
        l = l.replace(u"(多媒体，音乐教室)", "")
        l = l.replace(u"(科创专用教室)", "")
        l = l.replace(u"(网络五边语音)", "")
        l = l.replace(u"(网络五边菱)", "")
        l = l.replace(u"(长方无黑板)", "")
        l = l.replace(u"(五边菱形)", "")
        l = l.replace(u"(六边圆形)", "")
        l = l.replace(u"(网络六边)", "")
        l = l.replace(u"(网络五边)", "")
        l = l.replace(u"(传统语音)", "")
        l = l.replace(u"(长方形)", "")
        l = l.replace(u"(语音)", "")
        l = l.replace(u"(成多)", "")
        l = l.replace(u"(普)", "")
        l = l.replace(u"(多)", "")
        l = l.replace("*", "")
        return l

    def get_lessons(self, time_texts, locations, semester_text):
        """parse lesson"""
        ''' - parse time'''
        lessons = []
        for time_text in time_texts:
            '''parse week'''
            odd_or_even = self.parse_odd_or_even(time_text)

            '''sometimes, lesson has its own semester text'''
            semester = self.get_semester_from_time(time_text)
            if semester:
                weeks = week_data[semester][odd_or_even]
            else:
                weeks = week_data[semester_text][odd_or_even]

            number = re.findall("\d{1,2}", time_text[3:])
            if time_text:
                weekday = re.search(u"周(.)", time_text).group(1)
                lessons.append({
                    'day': chinese_weekdays[weekday],
                    'start': int(number[0]),
                    'end': int(number[-1]),
                    'weeks': weeks,
                })
            else:
                lessons.append({})

        ''' - parse location'''
        locations = map(self.trim_location, locations)
        if len(locations) > 1:
            '''each lesson has different location'''
            for i in range(len(lessons)):
                if lessons[i]:
                    try:
                        lessons[i]['location'] = locations[i]
                    except IndexError:
                        pass
        elif len(locations) == 1:
            '''lessons share the same location'''
            for l in lessons:
                if l:
                    l['location'] = locations[0]

        lessons = filter(bool, lessons)
        '''deal w/ special case: one lesson separated to two'''
        lessons = sorted(lessons, key=lambda x: (x['day'], x['start']))
        for i in range(1, len(lessons)):
            if (lessons[i]['day'] == lessons[i - 1]['day'] and
               lessons[i]['start'] == lessons[i - 1]['end'] + 1 and
               lessons[i]['location'] == lessons[i - 1]['location']):
                if lessons[i]['weeks'] == lessons[i - 1]['weeks']:
                    lessons[i - 1]['end'] = lessons[i]['end']
                    lessons[i]['delete'] = True
                elif len(lessons[i - 1]['weeks']) < len(lessons[i]['weeks']):
                    lessons[i - 1]['end'] = lessons[i]['end']
                    lessons[i]['weeks'] = list(set(lessons[i]['weeks']) - set(lessons[i - 1]['weeks']))
                else:
                    lessons[i]['start'] = lessons[i - 1]['start']
                    lessons[i - 1]['weeks'] = list(set(lessons[i - 1]['weeks']) - set(lessons[i]['weeks']))
        lessons = filter(lambda x: 'delete' not in x, lessons)
        return lessons

    def _setup(self):
        self.username = _misc.username
        self.password = _misc.password

    def _login(self):
        """
        完成登录，返回EasyLogin的对象a
        """
        self._setup()
        #a= EasyLogin(proxy="http://127.0.0.1:8080") #for burp suite debug
        a = EasyLogin()
        a.get(self.url_prefix + "default2.aspx")
        VIEWSTATE = a.VIEWSTATE()
        r_login = a.post(self.url_prefix +"/default2.aspx",
                         data = '__EVENTTARGET=Button1&__EVENTARGUMENT=&__VIEWSTATE={}&TextBox1={}&TextBox2={}&Textbox3=&RadioButtonList1=%BD%CC%CA%A6&Text1='.format(VIEWSTATE, self.username, self.password))

        result = re.match(
            "<script language='javascript'>alert\('(.{,300})'\);</script>", r_login.content)
        if result:
            msg = result.group(1).decode(self.charset)
            if msg == u"验证码不正确！！":
                raise LoginError("登录需要验证码，如果您不幸遇到了这个问题，请与我联系： QQ1535454882")
            if msg == u"用户名不存在！！":
                raise LoginError("Wrong Student ID")
            if msg[:4] == u"密码错误":
                raise LoginError("Wrong Password")
            if u"学号访问" in msg:
                raise LoginError("教务网控制学号访问，请稍后再试")
            raise LoginError("Unknown error: "+msg)
        if "zdy.htm?aspxerrorpath" in r_login.content:
            raise LoginError("Cannot login to jwbinfosys.zju.edu.cn, please retry later")
        content = r_login.content.decode(self.charset)

        print("Logged in successfully.")
        return a

    def get_exams(self, rows):
        exams = []
        for r in rows:
            if r.has_attr('class') and r['class'] == ["datagridhead"]:
                continue
            cols = r.select("td")
            time_texts = cols[6].get_text(strip=True)
            if not time_texts: #跳过考试时间空缺的考试
                continue

            time_pattern = "%Y年%m月%d日%H:%M"
            time_parse = re.split('[-)(]', time_texts.encode('utf-8'))
            time_start = datetime.strptime(time_parse[0]+time_parse[1], time_pattern)
            time_end = datetime.strptime(time_parse[0]+time_parse[2], time_pattern)

            course = {
                'original_id': cols[0].get_text(strip=True),
                'name': cols[1].get_text(strip=True),
                'credit': cols[2].get_text(strip=True),
                'location': cols[7].get_text(strip=True),
                'seat': cols[8].get_text(strip=True),
                'start': time_start.replace(tzinfo=timezone('Asia/Shanghai')),
                'end': time_end.replace(tzinfo=timezone('Asia/Shanghai'))
            }
            exams.append(course)
        return exams

    def run_exam(self, a):
        url_exam = self.url_prefix + "xskscx.aspx?xh=" + self.username
        r_exam = a.get(url_exam, o=True)
        open("test2.txt","wb").write(r_exam.content)
        exams = []

        if u"调查问卷".encode(self.charset) in r_exam.content:
            #raise GrabError("无法抓取您的课程，请先填写教务网调查问卷。")
            return []
        
        strainer = SoupStrainer("table", id="DataGrid1")
        soup = BeautifulSoup(r_exam.content.decode(self.charset),"html.parser", parse_only=strainer)
        rows = soup.select("tr")
        exams += self.get_exams(rows)
        data = """__EVENTTARGET=xqd&__EVENTARGUMENT=&__VIEWSTATE={VIEWSTATE}&xnd={exam_year}&xqd={xueqi}""".format(VIEWSTATE=a.VIEWSTATE(), exam_year=exam_year, xueqi=quote(exam_semester.encode(self.charset)))
        r_exam = a.post(url_exam, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded;'})
        open("test.txt","wb").write(r_exam.content)
        strainer = SoupStrainer("table", id="DataGrid1")
        soup = BeautifulSoup(r_exam.content.decode(self.charset), "html.parser",parse_only=strainer)
        rows = soup.select("tr")
        exams += self.get_exams(rows)
        return exams

    def run(self):
        a = self._login()

        url_course = self.url_prefix + "xskbcx.aspx?xh=" + self.username
        try:
            r_course = a.get(url_course, result=False, o=True)
        except Exception as e:
            e.print_exc()
            raise GrabError("抓取课表页面出错")
        if u"调查问卷".encode(self.charset) in r_course.content:
            raise GrabError("无法抓取您的课程，请先填写教务网调查问卷。")
        strainer = SoupStrainer("table", id="xsgrid")
        soup = BeautifulSoup(r_course.content.decode(self.charset),"html.parser", parse_only=strainer)
        rows = soup.select("tr")
        courses = []
        for r in rows:
            if r.has_attr('class') and r['class'] == ["datagridhead"]:
                continue

            cols = r.select("td")
            semester_text = cols[3].get_text(strip=True)
            time_texts = [text for text in cols[4].stripped_strings]
            locations = [text for text in cols[5].stripped_strings]
            lessons = self.get_lessons(time_texts, locations, semester_text)

            course = {
                'original_id': cols[0].get_text(strip=True),
                'name': cols[1].get_text(strip=True),
                'teacher': cols[2].get_text(strip=True),
                'lessons': lessons,
            }
            courses.append(course)
        try:
            return courses, self.run_exam(a)
        except:
            return courses, []


def gen_ical(packet):
    cal = Calendar()
    cal['version'] = '2.0'
    cal['prodid'] = '-//Zhejiang University//LIU Gengming+Chen Yuan//ZH'  # *mandatory elements* where the prodid can be changed, see RFC 5445
    courses = packet[0]
    exams = packet[1]

    for course in courses:
        for lesson in course['lessons']:
            weeks = lesson['weeks']
            for recur in weeks:
                event = Event()
                event.add('summary', unify_brackets(course['name']))
                offset_days = lesson['day'] - 1 + 7 * (int(recur) - 1)
                offset = timedelta(days=offset_days)
                classdate = week_start + offset
                start = lesson_time[lesson['start']]['start']
                end = lesson_time[lesson['end']]['end']
                event.add('dtstart', datetime.combine(classdate, start))
                event.add('dtend', datetime.combine(classdate, end))
                event.add('location', lesson['location'])
                event.add('description', u'教师：' + course['teacher'])
                event['uid'] = str(uuid1()) + '@ZJU'
                cal.add_component(event)

    for exam in exams:
        event = Event()
        event.add('summary', unify_brackets(exam['name']) + u' 考试')
        event.add('dtstart', exam['start'])
        event.add('dtend', exam['end'])
        event.add('location', exam['location']+' '+exam['seat'])
        event.add('description', u'学分：' + exam['credit'])
        event['uid'] = str(uuid1()) + '@ZJU'

        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('trigger', timedelta(days=-7))
        alarm.add('description', u'距离[%s]考试还有一周时间' % unify_brackets(exam['name']))
        alarm['uid'] = str(uuid1()) + '@ZJU'
        event.add_component(alarm)

        cal.add_component(event)

    return cal.to_ical()


def grabber(xh,password,outputfile=""):
    _misc.username = xh
    _misc.password = password
    _misc.output_file = outputfile if outputfile != "" else 'data/%s.ics' % xh
    grabber = TeapotParser()
    response = grabber.run() #可能抛出登录异常、需要搞定调查问卷的异常。。。调用者应该去捕获异常
    with open(os.path.join(os.path.dirname(__file__), _misc.output_file), 'w') as fout:
        fout.write(gen_ical(response))
    return "Dumped successfully."

if __name__ == "__main__":
    print('please import this file and use function grabber(xh,password,outputfile)')
