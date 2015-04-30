from flask import Flask, render_template, request
from pymongo import MongoClient
import pickle

app = Flask(__name__)

client = MongoClient()
mobile_privacy_research_db = client.mobile_privacy_research
requests_collection = mobile_privacy_research_db.requests
packages_collection = mobile_privacy_research_db.packages

@app.route("/")
def index():
    packages = packages_collection.find({})

    packages = sorted(packages, key=lambda k: len(k['requests_flagged']), reverse=True)
    return render_template('index.html', packages=packages)

@app.route("/detail")
def detail():
    package_title = request.args['package_title']
    package = packages_collection.find_one({"package_title" : package_title})

    for i, request_data in enumerate(package['requests_flagged']):
        package['requests_flagged'][i]['request'] = pickle.loads(request_data['request'])

    return render_template('detail.html', package=package)

if __name__ == "__main__":
    app.run(debug=True)
