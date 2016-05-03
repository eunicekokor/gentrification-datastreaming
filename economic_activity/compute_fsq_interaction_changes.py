import json
import argparse
import datetime as dt

from pymongo import MongoClient
from dateutil.relativedelta import relativedelta

parser = argparse.ArgumentParser()
parser.add_argument('duration')
args = parser.parse_args()
# acceptable values: {"oneyear", "twoyears"}
INTERVAL_LENGTH = args.duration

db_password = "macgregor0dewar"
db_user = "storyteller"
fsq_uri = "mongodb://{user}:{pw}@ds021850-a0.mlab.com:21850,ds021850-a1.mlab.com:21850/foursquare_venues?replicaSet=rs-ds021850".format(user=db_user, pw=db_password)
docp_uri = 'mongodb://{user}:{pw}@ds015690.mlab.com:15690/storytelling'.format(user=db_user, pw=db_password)
docp_client=MongoClient(docp_uri)
docp_coll_name = "neighborhoodsDOCP"
docp_coll = docp_client.get_database("storytelling").get_collection(docp_coll_name)
housing_client = MongoClient()
housing_db = housing_client.get_database("housing")
housing_change_coll = housing_db.get_collection(INTERVAL_LENGTH)
fsq_client = MongoClient(fsq_uri)
fsq_db = fsq_client.get_database("foursquare_venues")
fsq_change_coll = docp_client.get_database("storytelling").get_collection("fsq_interaction_changes")

DOCP_NEIGHBORHOODS = {}
for doc in docp_coll.find():
    if fsq_db.get_collection("_{}_interactions".format(doc["id"])):
        DOCP_NEIGHBORHOODS[doc["properties"]["NTAName"]] = doc["id"]
docp_to_zillow_mapfile = "docp_to_zillow_mapping.json"
with open(docp_to_zillow_mapfile, "r") as f:
    docp_to_zillow = json.loads(f.read())

# enumerate all time intervals
time_intervals = {
    "oneyear": {
        2010: (dt.datetime(2010, 1, 1), dt.datetime(2011, 1, 1)),
        2011: (dt.datetime(2011, 1, 1), dt.datetime(2012, 1, 1)),
        2012: (dt.datetime(2012, 1, 1), dt.datetime(2013, 1, 1)),
        2013: (dt.datetime(2013, 1, 1), dt.datetime(2014, 1, 1)),
        2014: (dt.datetime(2014, 1, 1), dt.datetime(2015, 1, 1)),
        2015: (dt.datetime(2015, 1, 1), dt.datetime(2016, 1, 1))
    },
    "twoyears": {
        2010: (dt.datetime(2010, 1, 1), dt.datetime(2012, 1, 1)),
        2011: (dt.datetime(2011, 1, 1), dt.datetime(2013, 1, 1)),
        2012: (dt.datetime(2012, 1, 1), dt.datetime(2014, 1, 1)),
        2013: (dt.datetime(2013, 1, 1), dt.datetime(2015, 1, 1)),
        2014: (dt.datetime(2014, 1, 1), dt.datetime(2016, 1, 1))
    }
}

preceding_intervals = {
    "oneyear":  {
        (dt.datetime(2010, 1, 1), dt.datetime(2011, 1, 1)): None,
        (dt.datetime(2011, 1, 1), dt.datetime(2012, 1, 1)): (dt.datetime(2010, 1, 1), dt.datetime(2011, 1, 1)),
        (dt.datetime(2012, 1, 1), dt.datetime(2013, 1, 1)): (dt.datetime(2011, 1, 1), dt.datetime(2012, 1, 1)),
        (dt.datetime(2013, 1, 1), dt.datetime(2014, 1, 1)): (dt.datetime(2012, 1, 1), dt.datetime(2013, 1, 1)),
        (dt.datetime(2014, 1, 1), dt.datetime(2015, 1, 1)): (dt.datetime(2013, 1, 1), dt.datetime(2014, 1, 1)),
        (dt.datetime(2015, 1, 1), dt.datetime(2016, 1, 1)): (dt.datetime(2014, 1, 1), dt.datetime(2015, 1, 1))
    },
    "twoyears": {
        (dt.datetime(2010, 1, 1), dt.datetime(2012, 1, 1)): None,
        (dt.datetime(2011, 1, 1), dt.datetime(2013, 1, 1)): None,
        (dt.datetime(2012, 1, 1), dt.datetime(2014, 1, 1)): (dt.datetime(2010, 1, 1), dt.datetime(2012, 1, 1)),
        (dt.datetime(2013, 1, 1), dt.datetime(2015, 1, 1)): (dt.datetime(2011, 1, 1), dt.datetime(2013, 1, 1)),
        (dt.datetime(2014, 1, 1), dt.datetime(2016, 1, 1)): (dt.datetime(2012, 1, 1), dt.datetime(2014, 1, 1)),
    }
}

def belongs_to_interval(start, candidate_interval_start):
    if INTERVAL_LENGTH == "twoyears" and start.year in [2015, 2016]:
        return candidate_interval_start.year == 2014
    return start.year == candidate_interval_start.year

def save_change_for_interval(nname, 
                             earlier_count, 
                             later_count, 
                             interval_start, 
                             is_gentrification_interval, 
                             is_before):
    earlier_count = earlier_count if earlier_count > 0 else 1
    later_count = later_count if later_count > 0 else 1
    # compute percent change
    percent_change = (later_count - earlier_count)/float(earlier_count)
    doc = {"nname": nname, 
            "start": interval_start, 
            "is_gent_interval": is_gentrification_interval, 
            "interval_duration": INTERVAL_LENGTH}
    if is_before:
        doc["change_before"] = percent_change
    else:
        doc["change_during"] = percent_change
    fsq_change_coll.insert_one(doc)

def save_changes(nname, interval_start, is_gentrification_interval):
    fsq_interaction_collection = fsq_db.get_collection("_{}_interactions".format(DOCP_NEIGHBORHOODS[nname]))
    preceding_interval = None
    current_interval = None
    for candidate_interval in preceding_intervals[INTERVAL_LENGTH]:
        if belongs_to_interval(interval_start, candidate_interval[0]):
            preceding_interval = preceding_intervals[INTERVAL_LENGTH][candidate_interval]
            current_interval = candidate_interval
    # how much did foursquare interactions change between previous time interval
    # and this gentrification period?
    if preceding_interval:
        # query Foursquare user-generated data for this neighborhood and the preceding time interval
        preceding_interval_filter = {"$gte": preceding_interval[0], "$lt": preceding_interval[1]} 
        preceding_count = fsq_interaction_collection.find({"timestamp": preceding_interval_filter}).count()
        if preceding_count > 0:
            # query Foursquare user-generated data for this neighborhood and the current time interval
            current_interval_filter = {"$gte": current_interval[0], "$lt": current_interval[1]}
            during_count = fsq_interaction_collection.find({"timestamp": current_interval_filter}).count()
            save_change_for_interval(nname, preceding_count, during_count, current_interval[0], is_gentrification_interval, True)
    # how much did foursquare interactions change during this gentrification interval?
    current_start_filter = {"$gte": current_interval[0], "$lt": current_interval[0]+relativedelta(months=+3)}
    current_end_filter = {"$gte": current_interval[1]+relativedelta(months=-3), "$lt": current_interval[1]}
    interval_start_count = fsq_interaction_collection.find({"timestamp": current_start_filter}).count() 
    interval_end_count = fsq_interaction_collection.find({"timestamp": current_end_filter}).count() 
    save_change_for_interval(nname, interval_start_count, interval_end_count, current_interval[0], is_gentrification_interval, False)

# compute changes for non-gentrification periods
for start_year in time_intervals[INTERVAL_LENGTH]:
    interval_start = time_intervals[INTERVAL_LENGTH][start_year][0]
    interval_start_filter = {"$gte": dt.datetime(start_year, 01, 01, 0, 0, 0),"$lt": dt.datetime(start_year, 02, 01, 0, 0, 0)}
    for docp_name in DOCP_NEIGHBORHOODS: 
        try:
            zillow_names = docp_to_zillow[docp_name]
            for zname in zillow_names:
                query = {"name": zname, "start": interval_start_filter}
                if housing_change_coll.find(query).count() == 0:
                    save_changes(docp_name, interval_start, False)
                else:
                    save_changes(docp_name, interval_start, True)
        except KeyError:
            save_changes(docp_name, interval_start, False)
