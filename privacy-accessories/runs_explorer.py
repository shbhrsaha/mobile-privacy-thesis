"""
    Browse runs raw data in Terminal
"""

import sys
import cgi
import socket
import urlparse
import pickle
import logging
from pymongo import MongoClient

logging.basicConfig(format='%(message)s', level=logging.DEBUG, filename='runs.log')

RUN_ID = int(sys.argv[1])

client = MongoClient()
mobile_privacy_research_db = client.mobile_privacy_research
runs = mobile_privacy_research_db.runs
packages = mobile_privacy_research_db.packages

def log(message):
    logging.info(message)

res = runs.find({"run_id" : RUN_ID})
for doc in res:
    run = doc
    package_title = run["package_title"]
requests = [pickle.loads(x) for x in run["requests"]]

for request in requests:
    method = request.method
    scheme = request.scheme
    host = request.host
    path = request.path
    content = request.content
    headers = request.headers


    url = scheme + "://" + host + path
    url_data_dict = cgi.parse_qs(urlparse.urlparse(url).query)

    # go one level deeper for doubleclick data
    temp_url_data_dict = url_data_dict.copy()
    for key, value in url_data_dict.iteritems():
        try:
            if len(value) == 1:
                parsed = cgi.parse_qs(value[0])
                if parsed:
                    del temp_url_data_dict[key]
                    temp_url_data_dict.update(parsed)
        except:
            continue
    url_data_dict = temp_url_data_dict

    content_data_dict = cgi.parse_qs(content)

    if url_data_dict or content_data_dict:
        try:
            url_data_tosave = {unicode(key, "latin-1").encode('ascii', 'replace').replace('\x00', '').replace(".","").replace("$",""): [unicode(x, "latin-1").encode('ascii', 'replace') for x in value] for (key, value) in url_data_dict.items()}
        except:
            url_data_tosave = {}

        try:
            content_data_tosave = {unicode(key, "latin-1").encode('ascii', 'replace').replace('\x00', '').replace(".","").replace("$",""): [unicode(x, "latin-1").encode('ascii', 'replace') for x in value] for (key, value) in content_data_dict.items()}
        except:
            content_data_tosave = {}

        keys = content_data_tosave.keys() + url_data_tosave.keys()


    print "==="
    print "Run ID: %s" % run["run_id"]
    print "Package: %s" % package_title
    print "Scheme: %s" % request.scheme
    print "Host: %s" % request.host
    print "Path: %s" % request.path
    print "Content: %s" % request.content
