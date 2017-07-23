# -*- coding: utf-8 -*-

import re

chinese_weekdays = {
    u'一': 1,
    u'二': 2,
    u'三': 3,
    u'四': 4,
    u'五': 5,
    u'六': 6,
    u'七': 7,
    u'日': 7,
    u'天': 7,
}



def unify_brackets(text):
    return re.sub(u'\((.{0,10})）', lambda(obj): u'（{0}）'.format(obj.group(1)), text)

''' 9.30  I think the script need these for begin:
BEGIN:VCALENDAR
METHOD:PUBLISH
VERSION:2.0
X-WR-CALNAME:l.dmxcsnsbh@gmail.com
PRODID:-//Apple Inc.//Mac OS X 10.9.4//EN
X-WR-CALDESC:l.dmxcsnsbh@gmail.com
X-APPLE-CALENDAR-COLOR:#2952A3
X-WR-TIMEZONE:Asia/Shanghai
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:Asia/Shanghai
BEGIN:STANDARD
TZOFFSETFROM:+0900
RRULE:FREQ=YEARLY;UNTIL=19910914T150000Z;BYMONTH=9;BYDAY=3SU
DTSTART:19890917T000000
TZNAME:GMT+8
TZOFFSETTO:+0800
END:STANDARD
BEGIN:DAYLIGHT
TZOFFSETFROM:+0800
DTSTART:19910414T000000
TZNAME:GMT+8
TZOFFSETTO:+0900
RDATE:19910414T000000
END:DAYLIGHT
END:VTIMEZONE
'''