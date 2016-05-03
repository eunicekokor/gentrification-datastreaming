import json
import requests
import os
import argparse
import datetime as dt

from collections import Counter
from pymongo import MongoClient

fsq_client_id = os.environ["FOURSQUARE_CLIENT_ID"]
fsq_client_secret = os.environ["FOURSQUARE_CLIENT_SECRET"]

parser = argparse.ArgumentParser()
parser.add_argument('batch')
args = parser.parse_args()
batch = int(args.batch)

db_password = "macgregor0dewar"
db_user = "storyteller"
fsq_uri = "mongodb://{user}:{pw}@ds021850-a0.mlab.com:21850,ds021850-a1.mlab.com:21850/foursquare_venues?replicaSet=rs-ds021850".format(user=db_user, pw=db_password)

fsq_client=MongoClient(fsq_uri)
fsq_db = fsq_client.get_database("foursquare_venues")

def convert_to_datetime(timestamp):
    return dt.datetime.utcfromtimestamp(timestamp)

def get_fsq_venue_interactions(venue_id):
    results = [] 
    try:
        try:
            photos_uri = "https://api.foursquare.com/v2/venues/{vid}/photos?limit=200&client_id={fid}&client_secret={fsecret}&v=20160410".format(vid=venue_id,fid=fsq_client_id,fsecret=fsq_client_secret)
            r = requests.get(photos_uri)
            response = json.loads(r.text)
            photos = response["response"]["photos"]["items"]
            for photo in photos:
                doc = {"timestamp": convert_to_datetime(photo["createdAt"]),
                        "venue_id": venue_id}
                results.append(doc)
        except IndexError:
            print "~~~~~ NO PHOTOS ~~~~~~"
        try:
            tips_uri = "https://api.foursquare.com/v2/venues/{vid}/tips?limit=200&client_id={fid}&client_secret={fsecret}&v=20160410".format(vid=venue_id,fid=fsq_client_id,fsecret=fsq_client_secret)
            r = requests.get(tips_uri)
            response = json.loads(r.text)
            tips = response["response"]["tips"]["items"]
            for tip in tips:
                doc = {"timestamp": convert_to_datetime(tip["createdAt"]),
                        "venue_id": venue_id}
                results.append(doc)
        except IndexError:
            print "~~~~~ NO TIPS ~~~~~~"
    except KeyError:
        print "!!!!!!!!!! KEY ERROR !!!!!!!!!"
        print response
        #raise
    return results

def venue_id_generator(neighborhood_id):
    coll = fsq_db.get_collection("_{}".format(neighborhood_id))
    for doc in coll.find():
        yield doc["venue_id"]

batch_filename = "batch{}.txt".format(batch)
neighborhood_ids = []
generators = []
with open(batch_filename, "r") as f:
    for neighborhood_id in f:
        nid = neighborhood_id.strip()
        # make sure this neighborhood hasn't been processed already
        coll = fsq_db.get_collection("_{}_interactions".format(nid))
        if coll.count() > 0:
            print "interactions already saved for neighborhood {}".format(nid)
        else:
            neighborhood_ids.append(nid)
            generators.append(venue_id_generator(nid))

num_generators = len(generators)
i = 0
num_exhausted = set()
while len(num_exhausted) < num_generators:
    gen = generators[i%num_generators]
    try:
        venue_id = next(gen)
        neighborhood_id = neighborhood_ids[i%num_generators]
        interactions = get_fsq_venue_interactions(venue_id) 
        if interactions:
            coll = fsq_db.get_collection("_{}_interactions".format(neighborhood_id))
            coll.insert_many(interactions)
            print "inserted {num_docs} into _{nid}_interactions".format(num_docs=len(interactions), nid=neighborhood_id)
    except StopIteration:
        if (i%num_generators) not in num_exhausted:
            print "!!!!!!! exhausted neighborhoodid: {}".format(neighborhood_ids[i%num_generators])
            num_exhausted.add(i%num_generators)
    i += 1
