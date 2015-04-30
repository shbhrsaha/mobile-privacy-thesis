"""
    Discovers and downloads new apps from the Play Store

    Must run in apk-downloader/ directory

    Prints the top packages to top_packages.log
"""

import os
import logging
import subprocess
import sys

CRAWLER_COMMAND = "java -jar /home/google-play-crawler/googleplay/googleplaycrawler-0.3.jar --conf /.crawler.conf"

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

def log(message):
    logging.info(message)

def run_and_fetch(cmd):
    """
        Runs cmd and returns the lines of output as a list
    """
    p = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.split("\n")

def download_package(packagename):
    cmd = "%s download %s" % (CRAWLER_COMMAND, packagename)
    p = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out
    print err

def top_apps():
    top_packages = []
    counter = 0
    log("Discovering categories")
    categories = [line.split(";")[0] for line in run_and_fetch("%s categories" % CRAWLER_COMMAND) if "ID" not in line]

    for category in categories:
        log("Iterating over %s category" % category)
        package_data = run_and_fetch("%s list %s -s apps_topselling_free -n 100" % (CRAWLER_COMMAND, category))

        for line in package_data:
            line_split = line.split(";")
            if len(line_split) > 1:
                packagename = line_split[1]
                top_packages.append(packagename)
                if packagename not in existing_packages:
                    log("Downloading %s" % packagename)
                    download_package(packagename)
                    existing_packages.append(packagename)
                if counter % 10 == 0:
                    log("Writing top apps so far to disk")
                    with open('top_packages.log','w') as f:
                        f.write('\n'.join(top_packages))
                counter += 1

def dictionary_search():
    log("Searching store with dictionary")
    words = [line.replace("\n","") for line in open(crawl_type).readlines()]

    for word in words:
        log("WORD: %s" % word)
        package_data = run_and_fetch("%s search %s" % (CRAWLER_COMMAND, word))

        for line in package_data:
            line_split = line.split(";")
            if len(line_split) > 1:
                packagename = line_split[1]
                if packagename not in existing_packages:
                    log("Downloading %s" % packagename)
                    download_package(packagename)
                    existing_packages.append(packagename)

crawl_type = sys.argv[1]

log("Indexing existing packages")
existing_packages = [x[:-4] for x in os.listdir(".") if ".apk" in x]

if not existing_packages:
    warning = raw_input("No packages downloaded already. Are you sure you're in the apk-downloader folder? Press <Enter> if so: ")

if crawl_type == "top":
    top_apps()
else:
    dictionary_search()
