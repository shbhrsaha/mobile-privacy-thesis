"""
    Add value flags to MongoDB database
"""

import sys
from pymongo import MongoClient

client = MongoClient()
mobile_privacy_research_db = client.mobile_privacy_research
flags = mobile_privacy_research_db.flags

if sys.argv[1] == "add":
    flag_title = sys.argv[2]
    flag_value = sys.argv[3]

    flags.insert({"flag_title" : flag_title, "flag_value" : flag_value})
else:
    print "Command not recognized"
