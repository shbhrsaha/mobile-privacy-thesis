"""
    Flags instances of potential dangerous requests!
"""

import csv
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
packages = mobile_privacy_research_db.packages

def log(message):
    logging.info(message)

writer = csv.writer(sys.stdout)
for run in runs.find():
    package_title = run["package_title"]
    requests = [pickle.loads(x) for x in run["requests"]]

    for request in requests:
        if request.scheme == "http":
            if "password" in request.path or "password" in request.content:
                if run["run_id"] < 1428847822:
                    """
                    print "==="
                    print "Run ID: %s" % run["run_id"]
                    print "Package: %s" % package_title
                    print "Scheme: %s" % request.scheme
                    print "Host: %s" % request.host
                    print "Path: %s" % request.path
                    print "Content: %s" % request.content
                    """
                    writer.writerow([run["run_id"],package_title,request.scheme,request.host,request.path,request.content])
