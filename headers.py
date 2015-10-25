import json
import myql
import yahoo_oauth
import string
import logging
import sys
from datetime import datetime
from myql.utils import pretty_json, pretty_xml
from yahoo_oauth import OAuth1
from myql import MYQL
from sys import argv

def add_drop(ap, an, dp, dn, lg, oauth):
    # Strings to replace
    replacements = {'{team_key}':'348.l.'+lg+'.t.1', 
                '{player_key_add}':'348.p.'+ap, 
                '{player_key_drop}':'348.p.'+dp}
    
    # 248964 - '97 Knicks
    # 248978 - Salty Spitoon
    
    # Create temp.txt to be sent to Yahoo
    with open('add-drop.txt') as infile, open('temp.txt', 'w') as outfile:
        for line in infile:
            for src, target in replacements.iteritems():
                line = line.replace(src, target)
            outfile.write(line)
    
    # Open temp.txt and store contents to data
    with open("temp.txt") as infile:
        data = infile.read()
    
    # Set url
    #url = "http://fantasysports.yahooapis.com/fantasy/v2/league/348.l.248964/" \
    #        "transactions;team_key=348.l.248964.t.1;type=add"
    
    # Configure headers for xml payload
    headers = {'Content-Type': 'application/xml'}

    # Send POST request
    #r = oauth.session.post(url, data=data, headers=headers)
    
    if 200 <= r.status_code < 300:
    #if True:
        print "[+] " + an + " added"
        print "[-] " + dn + " dropped"
        print "[*] Transaction completed at: %s" % datetime.now()
    else:
        print "Halp! Something happened!!!"
        print "HTTP code %d" % r.status_code

def get_player_json(li, pid, yql):
    src = 'fantasysports.players.ownership'
            
    resp = yql.raw_query("select * from %s where " \
            "player_key='%s.p.%s' and league_key='%s.l.%s'" \
            % (src, li["game"], pid, li["game"], li["league"]))
    
    return resp
    
def get_standings(li, yql):
    src = 'fantasysports.leagues.standings'
    
    resp = yql.raw_query("select * from %s where " \
            "league_key='%s.l.%s'" % (src, li["game"], li["league"]))
    
    #print(pretty_json(resp.content))
    ldata = json.loads(resp.text)
    
    print "Standings:"
    #print ldata["query"]["results"]["league"]["standings"]["teams"]["team"][0]["name"]
    for i in range(0,12):
        #print str(i+1) + " " + \
        #    ldata["query"]["results"]["league"]["standings"]["teams"]["team"][i]["name"]
        print "%d: %s [ID: %s]" % (i+1, \
             ldata["query"]["results"]["league"]["standings"]["teams"]["team"][i]["name"], \
             ldata["query"]["results"]["league"]["standings"]["teams"]["team"][i]["team_id"])

def check_player(li, pid, yql):
    #resp = yql.raw_query("select * from fantasysports.players.ownership where player_key='348.p." + str(pid) + "' and league_key='348.l.248978'")
    resp = get_player_json(li, pid, yql)
    cdata = json.loads(resp.text)
    name = cdata["query"]["results"]["player"]["name"]["full"]
    ownership = cdata["query"]["results"]["player"]["ownership"]["ownership_type"]
    run = 0
    
    #print name + " is at: " + ownership
    
    if (ownership == "freeagents"):
        owned = 1
    elif (ownership == "waivers"):
        owned = 2
    else:
        # ownership = team
        owned = 3
    return name, owned

def loop(li, al, dl, yql, oauth, ctr):
    # Exit flag
    ctri = 0
    
    # Looping through the lists
    for i in range(0, len(al)):
        if al[i] == 0:
            continue
    
        print "Checking al[%s] @ %s" % (i, al[i])
        aname, aowned = check_player(li, al[i], yql)
        #print "al[%s] owned = %s" % (i, aowned)
        
        # Player is owned by team, remove from list
        if aowned == 3:
            print "[!] %s got taken!!" % aname
            al[i] = 0
        
        # Free Agent
        elif aowned == 1:
            ctrj = 0
            flag = 0 # only drop 1 player
            for j in range(0, len(dl)):
                # Confirm player is still on team
                if dl[j] == 0:
                    continue
                
                print "Checking dl[%s] @ %s" % (j, dl[j])
                dname, downed = check_player(li, dl[j], yql)
                
                #If player to drop still on team
                if downed == 3 and flag == 0:
                    #print "Trying to add " + aname + " and drop " + dname
                    add_drop(al[i], aname, dl[j], dname, li["league"], oauth)
                    al[i] = 0
                    dl[j] = 0
                    flag = 1
                elif downed == 3 and flag == 1:
                    ctrj += int(dl[j])
                else:
                    dl[j] = 0

            # Exit case if all players dropped
            if ctrj == 0:
                print "[*] Out of players to drop. Terminating..."           
                sys.exit()
        
        # Player is in waivers or already taken
        else:
            if (ctr % 30) == 0:
                print "[*] " + aname + " is at: waivers"
            ctri += int(al[i])
    
    # Exit case if all players to add are taken
    if ctri == 0:
        print "[*] Out of players to add. Terminating..."
        sys.exit()
        
    ctr += 1


def main(li, al, dl, yql, oauth, ctr):
    if not oauth.token_is_valid():
        oauth.refresh_access_token()
    
    if ctr > 1 and (ctr % 30) == 0:
        #print print "[*] added @ %s" % datetime.now()
        print "[*] Running for %d minutes" % ctr
    elif ctr == 0:
        print "[*] Starting at: %s" % datetime.now()

    loop(li, al, dl, yql, oauth, ctr)
