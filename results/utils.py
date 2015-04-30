
import pickle
from pymongo import MongoClient

client = MongoClient()
mobile_privacy_research_db = client.mobile_privacy_research
runs = mobile_privacy_research_db.runs
packages = mobile_privacy_research_db.packages

def fetch_filtered_requests(expression, limit=None, sort=False):
    """
        Prints network request data filtered by the desired expression
    """
    to_return = []
    counter = 0
    for run in runs.find():
        package_title = run["package_title"]
        requests = [pickle.loads(x) for x in run["requests"]]

        for request in requests:
            should_return = eval(expression)

            if should_return:
                to_return.append((run["run_id"], package_title, request))
                counter += 1

        if limit and counter >= limit:
            break

    if sort:
        to_return = sorted(to_return, key=lambda x: x[0])

    return to_return

def print_requests(requests_data, limit=None):
    """
        Prints requests data
    """
    if not requests_data:
        print "No requests given"

    counter = 0
    for data in requests_data:
        request = data[2]
        print "==="
        print "Run ID: %s" % data[0]
        print "Package: %s" % data[1]
        print "Scheme: %s" % request.scheme
        print "Host: %s" % request.host
        print "Path: %s" % request.path
        print "Content: %s" % request.content

        counter += 1

        if limit and counter > limit:
            break
