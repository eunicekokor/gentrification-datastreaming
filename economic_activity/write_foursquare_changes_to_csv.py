import datetime as dt
from pymongo import MongoClient

db_password = "macgregor0dewar"
db_user = "storyteller"
storytelling_db_uri = 'mongodb://{user}:{pw}@ds015690.mlab.com:15690/storytelling'.format(user=db_user, pw=db_password)
client=MongoClient(storytelling_db_uri)
fsq_changes_coll_name = "fsq_interaction_changes"
fsq_changes_coll = client.get_database("storytelling").get_collection(fsq_changes_coll_name)

'''
# observations before gentrification periods
with open("fsq_gent_before_oneyear.csv", "w") as f:
    f.write("date,change\n")
    for doc in fsq_changes_coll.find({"is_gent_interval": True, "change_before": {"$exists": True}, "interval_duration": "oneyear"}):
        f.write("{dstring},{change}\n".format(dstring=doc["start"].strftime("%m/%d/%Y"), change=doc["change_before"]))
# observations during gentrification periods
with open("fsq_gent_during_oneyear.csv", "w") as f:
    f.write("date,change\n")
    for doc in fsq_changes_coll.find({"is_gent_interval": True, "change_during": {"$exists": True}, "interval_duration": "oneyear"}):
        f.write("{dstring},{change}\n".format(dstring=doc["start"].strftime("%m/%d/%Y"), change=doc["change_during"]))
# observations before non-gentrification periods
with open("fsq_nongent_before_oneyear.csv", "w") as f:
    f.write("date,change\n")
    for doc in fsq_changes_coll.find({"is_gent_interval": False, "change_before": {"$exists": True}, "interval_duration": "oneyear"}):
        f.write("{dstring},{change}\n".format(dstring=doc["start"].strftime("%m/%d/%Y"), change=doc["change_before"]))
# observations during non-gentrification periods
with open("fsq_nongent_during_oneyear.csv", "w") as f:
    f.write("date,change\n")
    for doc in fsq_changes_coll.find({"is_gent_interval": False, "change_during": {"$exists": True}, "interval_duration": "oneyear"}):
        f.write("{dstring},{change}\n".format(dstring=doc["start"].strftime("%m/%d/%Y"), change=doc["change_during"]))
'''

# observations before gentrification periods
with open("fsq_gent_before_twoyears.csv", "w") as f:
    f.write("date,change\n")
    for doc in fsq_changes_coll.find({"is_gent_interval": True, "change_before": {"$exists": True}, "interval_duration": "twoyears"}):
        f.write("{dstring},{change}\n".format(dstring=doc["start"].strftime("%m/%d/%Y"), change=doc["change_before"]))
# observations during gentrification periods
with open("fsq_gent_during_twoyears.csv", "w") as f:
    f.write("date,change\n")
    for doc in fsq_changes_coll.find({"is_gent_interval": True, "change_during": {"$exists": True}, "interval_duration": "twoyears"}):
        f.write("{dstring},{change}\n".format(dstring=doc["start"].strftime("%m/%d/%Y"), change=doc["change_during"]))
# observations before non-gentrification periods
with open("fsq_nongent_before_twoyears.csv", "w") as f:
    f.write("date,change\n")
    for doc in fsq_changes_coll.find({"is_gent_interval": False, "change_before": {"$exists": True}, "interval_duration": "twoyears"}):
        f.write("{dstring},{change}\n".format(dstring=doc["start"].strftime("%m/%d/%Y"), change=doc["change_before"]))
# observations during non-gentrification periods
with open("fsq_nongent_during_twoyears.csv", "w") as f:
    f.write("date,change\n")
    for doc in fsq_changes_coll.find({"is_gent_interval": False, "change_during": {"$exists": True}, "interval_duration": "twoyears"}):
        f.write("{dstring},{change}\n".format(dstring=doc["start"].strftime("%m/%d/%Y"), change=doc["change_during"]))
