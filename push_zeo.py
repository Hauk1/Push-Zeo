#!/usr/bin/env python2.7

import base64
import json
import urllib2

from datetime import date, timedelta

# Look at the last n days on each run. Update number as needed
DAYS_TO_GATHER = 14

# Your Zeo API key, which you can request here: http://mysleep.myzeo.com/api/signup.php
ZEO_API_KEY = ""


# The domain youd tie your Zeo API key to (their API checks the referer)
ZEO_API_DOMAIN = ""


# Your Zeo credentials 
print "Enter email"
ZEO_USER = raw_input(">")
print "Enter password"
ZEO_PASSWORD = raw_input(">")

# The URL we're querying for a Zeo sleep data record
ZEO_URL = "https://api.myzeo.com:8443/zeows/api/v1/json/sleeperService/getSleepRecordForDate?key=%s&date=" % ZEO_API_KEY

def get_zeo(date):
    """Get a sleep record from Zeo by date"""

    request = urllib2.Request(ZEO_URL + date, None)

    request.add_header('Referer', ZEO_API_DOMAIN)

    auth_string = base64.encodestring('%s:%s' % (ZEO_USER, ZEO_PASSWORD)).replace('\n', '')

    request.add_header("Authorization", "Basic %s" % auth_string)

    stream = urllib2.urlopen(request)

    data = {}

    try:
        data = json.load(stream)
    except ValueError:
        print "Wasn't able to parse the result from Zeo as JSON."

        return False

    return { "data": [{
        "obj": {
            "id": date,
            "date": date,
            "record": data
        }
    }]}

def main():
    today = date.today()

    for i in xrange(DAYS_TO_GATHER):
        day = today - timedelta(days=i)

        zeo_data = get_zeo(day.strftime("%Y-%m-%d"))

        if zeo_data:
            print zeo_data

if __name__ == "__main__":
    main()
