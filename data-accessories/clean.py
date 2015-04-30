"""
    Removes extra data from runs collection
"""

import sys
import cgi
import socket
import urlparse
import pickle
import logging
from pymongo import MongoClient

logging.basicConfig(format='%(message)s', level=logging.DEBUG, filename='runs.log')

client = MongoClient()
mobile_privacy_research_db = client.mobile_privacy_research
runs = mobile_privacy_research_db.runs

counter = 0
for run in runs.find():
    requests = [pickle.loads(x) for x in run["requests"]]

    filtered_requests = [x for x in requests if x.host != "android.clients.google.com"]

    filtered_requests = [pickle.dumps(x) for x in filtered_requests]

    run["requests"] = filtered_requests

    runs.save(run)

    if counter % 10 == 0:
        print counter

    counter += 1
