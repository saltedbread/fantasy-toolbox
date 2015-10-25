#!/usr/bin/env python

from apscheduler.schedulers.blocking import BlockingScheduler
from headers import *

# disable logs
logging.disable(logging.CRITICAL)


### Python is pass-by-reference

# Set oauth credentials
oauth = OAuth1(None, None, from_file="credentials.json")

# Set yql response type: JSON
yql = MYQL(format="json", oauth=oauth)

#url = "http://fantasysports.yahooapis.com/fantasy/v2/league/348.l.248978/" \
#        "transactions;team_key=348.l.248978.t.1;type=add"
league_info = {'game':'348', # 348 = NFL15
                'league':argv[1], 
                'team':argv[2]}

# 248964 - '97 Knicks
# 248978 - Salty Spitoon

#url = "http://fantasysports.yahooapis.com/fantasy/v2/league/348.l.248978/" \
#            "transactions;team_key=%s.l.%s.t.%s;type=add" % \
#            (league_info["game"], league_info["league"], league_info["team"])

#print url

#get_standings(league_info, yql)
# time counter
ctr = 0

# Initialize add and drop lists
add_list = list()
drop_list = list()

# Fill up lists from ta.txt and td.txt
with open('ta.txt') as infile:
    add_list = infile.read().splitlines()

with open('td.txt') as infile:
    drop_list = infile.read().splitlines()

print "[*] Starting fantasy-toolbox"
#print "[*] Main loop will start in 2015-10-21 02:58:00"

main(league_info,add_list,drop_list,yql,oauth,ctr)

# Set scheduler
#start_date = '2015-10-21 02:58:00'
#scheduler = BlockingScheduler()
#scheduler.add_job(main, 'interval', start_date=start_date, minutes=1, args=[league_info,add_list,drop_list,yql,oauth,ctr])
#try:
#    scheduler.start()
#except (KeyboardInterrupt, SystemExit):
#    pass
