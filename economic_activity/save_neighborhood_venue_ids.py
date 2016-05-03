import json
import requests
import os
import argparse

from collections import Counter
from pymongo import MongoClient

fsq_client_id = os.environ["FOURSQUARE_CLIENT_ID"]
fsq_client_secret = os.environ["FOURSQUARE_CLIENT_SECRET"]

parser = argparse.ArgumentParser()
parser.add_argument('neighborhood_id')
args = parser.parse_args()
msg = int(args.neighborhood_id)

db_password = "macgregor0dewar"
db_user = "storyteller"
fsq_uri = "mongodb://{user}:{pw}@ds021850-a0.mlab.com:21850,ds021850-a1.mlab.com:21850/foursquare_venues?replicaSet=rs-ds021850".format(user=db_user, pw=db_password)
docp_uri = 'mongodb://{user}:{pw}@ds015690.mlab.com:15690/storytelling'.format(user=db_user, pw=db_password)

fsq_client=MongoClient(fsq_uri)
fsq_db = fsq_client.get_database("foursquare_venues")
fsq_coll_name = "_{}".format(msg)
fsq_coll = fsq_db.get_collection(fsq_coll_name)

docp_client=MongoClient(docp_uri)
docp_db = docp_client.get_database("storytelling")
docp_coll_name = "neighborhoodsDOCP"
docp_coll = docp_db.get_collection(docp_coll_name)

def testLoc(lon, lat):
    q={ "geometry": { "$geoIntersects": { "$geometry": { "type": "Point", "coordinates": [ lon, lat ] } } } }
    geoJSON = docp_coll.find_one(q)
    if not geoJSON:
        return None
    neighborhood = geoJSON['properties']['NTAName']
    borough = geoJSON['properties']['BoroName']
    return [neighborhood, borough]

# get centroid for this neighborhood, which we treat as source of bfs
source_neighborhood = docp_coll.find_one({"id": int(msg)})
source_lon, source_lat = source_neighborhood["centroid"]["coordinates"]
source_neigh_name = source_neighborhood['properties']['NTAName']
source_borough_name = source_neighborhood['properties']['BoroName']

def insert_in_correct_collection(matched_neighborhood, matched_borough, doc, cnt):
    if matched_neighborhood == source_neigh_name and matched_borough == source_borough_name:
        if fsq_coll.find_one({"venue_id":doc["venue_id"]}):
            print "duplicate"
        else:
            fsq_coll.insert_one(doc)
            cnt[msg] += 1
    else:
        # find out id of the neighborhood this matches
        for potential_actual in docp_coll.find({"properties.NTAName": matched_neighborhood}):
            if potential_actual['properties']['BoroName'] == matched_borough:
                match_coll = fsq_db.get_collection("_{}".format(potential_actual["id"]))
                if match_coll.find_one({"venue_id":doc["venue_id"]}):
                    print "duplicate"
                else:
                    match_coll.insert_one(doc)
                    cnt[potential_actual["id"]] += 1
    return cnt

cnt = Counter()
uri = "https://api.foursquare.com/v2/venues/explore?limit=50&ll={lat},{lon}&client_id={fid}&client_secret={fsecret}&v=20160410".format(lat=source_lat,lon=source_lon,fid=fsq_client_id,fsecret=fsq_client_secret)
r = requests.get(uri)
response = json.loads(r.text)
for item in response["response"]["groups"][0]["items"]:
    doc = {"venue_id": item["venue"]["id"],
            "lat": item["venue"]["location"]["lat"],
            "lon": item["venue"]["location"]["lng"],
            "categories": [cat["name"] for cat in item["venue"]["categories"]],
            "num_checkins": item["venue"]["stats"]["checkinsCount"],
            "num_tips": item["venue"]["stats"]["tipCount"],
            "explored": False
          }
    match = testLoc(doc["lon"], doc["lat"])
    if not match:
        continue
    matched_neighborhood, matched_borough = match
    insert_in_correct_collection(matched_neighborhood, matched_borough, doc, cnt)

def fsq_venue_search(lat, lon):
    uri = "https://api.foursquare.com/v2/venues/search?limit=50&radius=2000&ll={lat},{lon}&client_id={fid}&client_secret={fsecret}&v=20160410".format(lat=lat,lon=lon,fid=fsq_client_id,fsecret=fsq_client_secret)
    r = requests.get(uri)
    response = json.loads(r.text)
    try:
        venues = response["response"]["venues"]
        return venues
    except KeyError:
        print response
        return []

num_api_calls = 0
while num_api_calls <= 50:
    doc = fsq_coll.find_one({"explored": False})
    venues = fsq_venue_search(doc["lat"], doc["lon"])
    for venue in venues:
        doc = {"venue_id": venue["id"],
                "lat": venue["location"]["lat"],
                "lon": venue["location"]["lng"],
                "categories": [cat["name"] for cat in venue["categories"]],
                "num_checkins": venue["stats"]["checkinsCount"],
                "num_tips": venue["stats"]["tipCount"],
                "explored": False
        }
        match = testLoc(doc["lon"], doc["lat"])
        if not match:
            continue
        matched_neighborhood, matched_borough = match
        counter = insert_in_correct_collection(matched_neighborhood, matched_borough, doc, cnt)
    fsq_coll.update({"venue_id": doc["venue_id"]},{"$set": {"explored": True}})
    num_api_calls += 1
print counter
