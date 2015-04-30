"""
    Synchronizes packages collection with data from runs collection
"""

import cgi
import pickle
import socket
import logging
import urlparse
from pymongo import MongoClient

logging.basicConfig(format='%(message)s', level=logging.DEBUG, filename='runs.log')

client = MongoClient()
mobile_privacy_research_db = client.mobile_privacy_research
runs = mobile_privacy_research_db.runs
packages = mobile_privacy_research_db.packages
flags = mobile_privacy_research_db.flags

def log(message):
    logging.info(message)

def ensure_package(package_title):
    """
        Returns the package object
        or creates it in the database
        if it doesn't already exist
    """
    package = packages.find_one({"package_title" : package_title})

    if not package:
        packages.save({
            "package_title" : package_title,
            "requests_flagged" : []
        })
        return packages.find_one({"package_title" : package_title})

    return package

def add_flag(package_title, flag, request):
    """
        Adds a flag to a package in the database
    """
    package = ensure_package(package_title)


    package["requests_flagged"].append({
        "flag" : flag,
        "host" : request.host,
        "request" : pickle.dumps(request)
    })

    packages.save(package)

log("Clearing existing packages")
packages.remove()

log("Retrieving value flags")
flag_values = flags.find()

total_run_count = runs.count()

counter = 0
for run in runs.find():
    log("Processing run %s of %s" % (counter, total_run_count))

    package_title = run["package_title"]
    run_id = run["run_id"]
    requests = [pickle.loads(x) for x in run["requests"]]

    package = ensure_package(package_title)

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

            keys = [x.lower() for x in content_data_tosave.keys() + url_data_tosave.keys()]
            values = [x for x in content_data_tosave.values() + url_data_tosave.values()]


            for flag in flag_values:
                if [flag['flag_value'].lower()] in values:
                    add_flag(package_title, flag['flag_title'], request)

            if any(x in keys for x in ["lat","latitude","userLat","location","zip"]):
                add_flag(package_title, "LOCATION", request)

            if any(x in keys for x in ["age","dob", "yob"]):
                add_flag(package_title, "AGE", request)

            if any(x in keys for x in ["gender"]):
                add_flag(package_title, "GENDER", request)

            if any(x in keys for x in ["platform", "cos", "os", "device", "device.model"]):
                add_flag(package_title, "PLATFORM", request)

            if any(x in keys for x in ["carrier", "device.carrier"]):
                add_flag(package_title, "CARRIER", request)

            if any(x in keys for x in ["mac", "macaddress", "mac_address"]):
                add_flag(package_title, "MAC", request)

            if any(x in keys for x in ["email"]):
                add_flag(package_title, "EMAIL", request)

    counter += 1
