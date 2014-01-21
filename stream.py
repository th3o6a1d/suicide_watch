# coding: utf-8
from TwitterAPI import TwitterAPI
import json 
import httplib
import sqlite3 
import sys

### Credentials are saved in .json configuration file.  Obtain your credentials from dev.twitter.com.  
a = open('credentials.json','r')
f = json.load(a)

### Initialize the API
api = TwitterAPI(f['consumer_key'], f['consumer_secret'], f['access_token'], f['access_token_secret'])

### Create sqlite3 database
con = sqlite3.connect('redflags_stream.db')
con.text_factory = str
cur = con.cursor()  

### Access the stream.  Filter by location.  Current location is New York City. 
stream = api.request('statuses/filter',{'language':'en','locations':'-74,40,-73,41'})
 
### Wordlist is from Argyle, Trenton et al. "Tracking Suicide Risk Factors Through Twitter in the US."  Crisis 2014; Vol. 35(1):51–59.
wordlist = ["Me abused depressed", "me hurt depressed", "feel hopeless depressed", "feel alone depressed", "I feel helpless", "I feel worthless", "I feel sad", "I feel empty", "I feel anxious", "sleeping \"a lot\" lately", "I feel irritable", "I feel restless", "depressed alcohol", "sertraline", "zoloft", "prozac", "pills depressed", "suicide once more", "me abused suicide", "pain suicide", "I\'ve tried suicide before", "mom suicide tried", "sister suicide tried", "brother suicide tried", "friend suicide", "suicide attempted sister", "suicide thought about before", "thought suicide before", "had thoughts suicide", "had thoughts killing myself", "used thoughts suicide", "once thought suicide", "past thoughts suicide", "multiple thought suicide", "stop cutting myself", "I\'m being bullied", "I\'ve been cyber bullied", "feel bullied I\'m", "stop bullying me", "keeps bullying me", "always getting bullied", "gun suicide", "shooting range went", "gun range my", "I was diagnosed schizophrenia", "been diagnosed anorexia", "diagnosed bulimia", "I diagnosed OCD", "I diagnosed bipolar", "I diagnosed PTSD", "diagnosed borderline personality disorder", "diagnosed panic disorder", "diagnosed social anxiety disorder", "dad fight again", "parents fight again", "I impulsive"]

### Looks for redflag phrases and dumps them in db and txt format
for tweet in stream.get_iterator():
    try: 
        name = tweet['user']['name'].encode("utf-8", errors='ignore')
        screen_name = tweet['user']['screen_name'].encode("utf-8", errors='ignore')
        tweet_text = tweet['text'].encode("utf-8", errors='ignore')
        lat = tweet['coordinates']['coordinates'][1]
        lng = tweet['coordinates']['coordinates'][0]
            
        print "Name: " + name
        print "Screename: " + screen_name
        print tweet_text
        
        for i in wordlist:
            if i in tweet_text:
            ### Tweet has been flagged.
            ### 1.  Reverse Geocode
                try:
                    conn = httplib.HTTPConnection("maps.googleapis.com")
                    conn.request("GET", "http://maps.googleapis.com/maps/api/geocode/json?latlng="+str(lat)+","+str(lng)+"&sensor=true")
                    r = conn.getresponse()
                    geodata = json.load(r)
                    a = geodata['results'][0]['formatted_address']
                    address = a.encode("utf-8", errors='ignore')
                    print "Address: " + address
                except:
                    address = ""
                    print "Reverse Geocode Failed"           
                
            ### 2.  Lookup user's past tweets.  Sum up the times a redflag word is used in user's last 500 tweets.  
                try:
                    r = api.request('statuses/user_timeline', {'screen_name':screen_name,'count':'500'})
                    word_count = 0
                    for item in r.get_iterator():
                        for i in wordlist:
                            if i in item['text']:
                                word_count += 1                            
                        followers = int(item['user']['followers_count'])
                    print "Word Count: " + str(word_count)
                    print "Followers Count: " + str(followers)
                except:
                    print "REST Lookup of user failed"
                
            ### 3. Write output to text file.
                try: 
                    with open('redflags_stream.txt','a') as output_file:
                        output_file.write("Name: "+ name + "\n" + 
                        "Screen_Name: " + screen_name +"\n" + 
                        "Address: " + address + "\n" + 
                        "Flagged Tweet: " + tweet_text +"\n" + 
                        "Word Count: " + str(word_count)+ "\n" + 
                        "Followers Count: " + str(followers) +"\n"+"\n")
                except:
                    print "Writing to text file failed"
           
           ### 4. Write output to database
                try:
                    cur.executescript("""
                    DROP TABLE IF EXISTS Tweets;
                    CREATE TABLE Tweets(ID PRIMARY KEY NULL, Name TEXT, Screen_Name TEXT, Address TEXT, Latitude FLOAT, Longitude FLOAT, Tweet_Text TEXT, Word_Count INT, Followers INT);
                    """)
                    cur.execute("""INSERT INTO Tweets (Name, Screen_Name, Address, Latitude, Longitude, Tweet_Text, Word_Count, Followers) VALUES(?,?,?,?,?,?,?,?)""", (name, screen_name, address, lat, lng, tweet_text, word_count, followers))
                    con.commit()
                except:
                    print "Writing to db failed"
                break    
    except:
        print "Waiting for tweets"
    print ""

