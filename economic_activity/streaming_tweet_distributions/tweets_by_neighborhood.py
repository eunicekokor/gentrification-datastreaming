import redis
import time
import json
import os
import logging

from pymongo import MongoClient, GEOSPHERE
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

ttl = 60 * 60	# one hour
consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

logger = logging.getLogger('myapp')
hdlr = logging.FileHandler(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tweets_by_neighborhood.log'))
hdlr.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)

def testLoc(lon, lat):
    q={ "geometry": { "$geoIntersects": { "$geometry": { "type": "Point", "coordinates": [ lon, lat ] } } } }
    geoJSON = coll.find_one(q)
    if not geoJSON:
        return None
    neighborhood = geoJSON['properties']['NTAName'] 
    borough = geoJSON['properties']["BoroName"]
    return "{n}/{b}".format(n=neighborhood, b=borough)

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    """
    def on_data(self, data):
        status = json.loads(data) 
        if status["geo"]:
            coord = status["geo"]["coordinates"]
            neighborhood = testLoc(coord[1], coord[0])
            if neighborhood:
                conn.setex(time.time(), neighborhood, ttl)

    def on_error(self, status):
        logger.error(status)

if __name__ == '__main__': 
    conn = redis.Redis()
    db_password = "macgregor0dewar"
    db_user = "storyteller"
    uri = 'mongodb://{user}:{pw}@ds015690.mlab.com:15690/storytelling'.format(user=db_user, pw=db_password)
    client=MongoClient(uri)
    db=client.get_database("storytelling")
    coll_name = "neighborhoodsDOCP"
    coll=db.get_collection(coll_name)
    coll.create_index([("coordinates", GEOSPHERE)])
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)
    stream.filter(locations = [-74,40,-73,41])
