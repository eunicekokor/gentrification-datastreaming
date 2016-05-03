#!/usr/bin/env python

import json
import requests
import datetime as dt

from bson.codec_options import CodecOptions
from datetime import tzinfo, timedelta
from pymongo import MongoClient

'''
All the date processing logic is sourced from the example
implementation in the documentation of the `datetime`
module in Python's standard library
https://docs.python.org/2/library/datetime.html

'''

def first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt

# In the US, since 2007, DST starts at 2am (standard time) on the second
# Sunday in March, which is the first Sunday on or after Mar 8.
DSTSTART_2007 = dt.datetime(1, 3, 8, 2)
# and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
DSTEND_2007 = dt.datetime(1, 11, 1, 1)
# From 1987 to 2006, DST used to start at 2am (standard time) on the first
# Sunday in April and to end at 2am (DST time; 1am standard time) on the last
# Sunday of October, which is the first Sunday on or after Oct 25.
DSTSTART_1987_2006 = dt.datetime(1, 4, 1, 2)
DSTEND_1987_2006 = dt.datetime(1, 10, 25, 1)
# From 1967 to 1986, DST used to start at 2am (standard time) on the last
# Sunday in April (the one on or after April 24) and to end at 2am (DST time;
# 1am standard time) on the last Sunday of October, which is the first Sunday
# on or after Oct 25.
DSTSTART_1967_1986 = dt.datetime(1, 4, 24, 2)
DSTEND_1967_1986 = DSTEND_1987_2006
ZERO = timedelta(0)
HOUR = timedelta(hours=1)

class USTimeZone(tzinfo):
    def __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    def __repr__(self):
        return self.reprname

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            return ZERO
        assert dt.tzinfo is self

        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO
        start = first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = first_sunday_on_or_after(dstend.replace(year=dt.year))
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

if __name__ == "__main__":
    Eastern  = USTimeZone(-5, "Eastern",  "EST", "EDT")
    db_password = "macgregor0dewar"
    db_user = "storyteller"
    uri = 'mongodb://{user}:{pw}@ds015690.mlab.com:15690/storytelling'.format(user=db_user, pw=db_password)
    client=MongoClient(uri)
    db=client.get_database("storytelling")
    coll_name = "foo"
    coll=db.get_collection(coll_name).with_options(codec_options=CodecOptions(tz_aware=True,tzinfo=Eastern)) 
    r = requests.get('http://localhost:5000/distrib')
    doc = {"distribution": r.text, "time": dt.datetime.now(tz=Eastern)}
    coll.insert_one(doc) 
