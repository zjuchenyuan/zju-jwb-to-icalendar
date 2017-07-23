# -*- coding: utf-8 -*-

from datetime import date, time
from pytz import timezone


'''week_start and week_data ONLY FOR 2013-2014 second semester, should be updated every semester.
'''

# date of the first Monday
week_start_2013_2 = date(2014, 2, 24)
week_start_2014_1 = date(2014, 9, 22)
week_start_2014_2 = date(2015, 3, 9)
week_start_2015_1 = date(2015, 9, 14)
week_start_2015_2 = date(2016, 2, 29)
week_start_2016_1 = date(2016, 9, 12)
week_start_2016_2 = date(2017, 2, 27)
week_start_2017_1 = date(2017, 9, 18)
week_start_2017_2 = date(2018, 3, 5)


exam_year = '2017-2018' #记得改这里
week_start = week_start_2017_1  #记得改这里
exam_semester = u'1|冬'#可选：1|秋，1|冬，2|春，2|夏

week_data= {
    u"春": {
        "odd":  [1, 3, 5, 7],
        "even": [2, 4, 6, 8],
        "all":  [1, 2, 3, 4, 5, 6, 7, 8],
    },
    u"夏": {
        "odd":  [10, 12, 14, 16],
        "even": [11, 13, 15, 17],
        "all":  [10, 11, 12, 13, 14, 15, 16, 17],
    },
    u"春夏": {
        "odd":  [1, 3, 5, 7, 10, 12, 14, 16],
        "even": [2, 4, 6, 8, 11, 13, 15, 17],
        "all":  [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17],
    },
    u"秋": {
        "odd":  [1, 3, 5, 7],
        "even": [2, 4, 6, 8],
        "all":  [1, 2, 3, 4, 5, 6, 7, 8],
    },
    u"冬": {
        "odd":  [10, 12, 14, 16],
        "even": [11, 13, 15, 17],
        "all":  [10, 11, 12, 13, 14, 15, 16, 17],
    },
    u"秋冬": {
        "odd":  [1, 3, 5, 7, 10, 12, 14, 16],
        "even": [2, 4, 6, 8, 11, 13, 15, 17],
        "all":  [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17],
    },
}

def time_shanghai(h, m):
    return time(h, m, tzinfo=timezone('Asia/Shanghai'))

lesson_time = [
    {},
    {
        "start": time_shanghai(8, 0),
        "end": time_shanghai(8, 45),
    },
    {
        "start": time_shanghai(8, 50),
        "end": time_shanghai(9, 35),
    },
    {
        "start": time_shanghai(9, 50),
        "end": time_shanghai(10, 35),
    },
    {
        "start": time_shanghai(10, 40),
        "end": time_shanghai(11, 25),
    },
    {
        "start": time_shanghai(11, 30),
        "end": time_shanghai(12, 15),
    },
    {
        "start": time_shanghai(13, 15),
        "end": time_shanghai(14, 0),
    },
    {
        "start": time_shanghai(14, 5),
        "end": time_shanghai(14, 50),
    },
    {
        "start": time_shanghai(14, 55),
        "end": time_shanghai(15, 40),
    },
    {
        "start": time_shanghai(15, 55),
        "end": time_shanghai(16, 40),
    },
    {
        "start": time_shanghai(16, 45),
        "end": time_shanghai(17, 30),
    },
    {
        "start": time_shanghai(18, 30),
        "end": time_shanghai(19, 15),
    },
    {
        "start": time_shanghai(19, 20),
        "end": time_shanghai(20, 5),
    },
    {
        "start": time_shanghai(20, 10),
        "end": time_shanghai(20, 55),
    },
]
