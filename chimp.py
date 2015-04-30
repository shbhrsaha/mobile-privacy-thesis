"""
    Randomly clicks through requested apps and saves request data to MongoDB

    Usage:
        python chimp.py [profile.yml]
"""

import os
import sys
import subprocess
import time
import random
from uiautomator import Device
from multiprocessing.managers import BaseManager
import shlex
import yaml
import utils
from pymongo import MongoClient
import pickle

f = open(sys.argv[1], "r")
profile = yaml.load(f.read())

monkey_code = profile["monkey"]
monkey_folders = os.listdir("monkeys")

if monkey_code not in monkey_folders:
    raise RuntimeError("Monkey specified in profile does not exist.")

exec "import monkeys.%s.monkey as monkey_module" % monkey_code
monkey = monkey_module.Monkey(profile["parameters"])

if profile["measure_privacy"]:
    client = MongoClient(profile["host_ip"], profile["mongo_port"])
    mobile_privacy_research_db = client.mobile_privacy_research
    runs = mobile_privacy_research_db.runs

    BaseManager.register('get_queue')
    m = BaseManager(address=(profile["host_ip"], profile["request_queue_port"]), authkey='')
    m.connect()
    request_queue = m.get_queue()
    utils.clear_queue(request_queue)

# connect to ADB
d = Device(profile["device_id"])
utils.log("Connected to Android device")

apk_files = [x.replace("\n","") for x in open(profile["apk_list"]).readlines()]

for apk_file in apk_files:
    package_name = apk_file.replace("\n","")
    if "apk_dir" in profile:
        package_name = profile["apk_dir"] + "/" + package_name
    package_title = package_name.split("/")[-1].replace(".apk","")

    if "repeat" in profile and not profile["repeat"]:
        exists = runs.find_one({"package_title": package_title})
        if exists:
            if exists["requests"]:
                utils.log("Already recorded privacy and network data and repeat set to False. Continuing...")
                continue
            else:
                utils.log("Attempted before, but no network data found. Will not retry now...")
                continue

    utils.log("Checking if package %s exists... " % package_name)
    exists = False
    cmd = shlex.split("adb shell pm list packages %s" % package_title)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if package_title in out:
        utils.log("Package %s already exists. Skipping installation" % package_name)
        exists = True

    if not exists:
        utils.log("Attempting installation for %s" % package_name)
        try:
            subprocess.check_output(
                ['adb', '-s', profile["device_id"], 'install', package_name],
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as e:
            utils.log("Installation failed for %s. Aborting." % package_name)
            continue
        utils.log("Installation succeeded for %s" % package_name)

    if profile["measure_privacy"]:
        utils.clear_queue(request_queue)

    run_id = int(time.time())
    utils.log("Running monkey on %s" % package_name)
    utils.log("(Run ID: %s)" % run_id)
    try:
        monkey.run(d, package_title, profile["parameters"])
    except Exception as e:
        raise
        utils.log(e)
        utils.log("Monkey failed for %s. Aborting." % package_name)
        continue
    utils.log("Monkey succeeded for %s" % package_name)

    # to avoid sorry dialog when uninstalling
    d.press.home()
    subprocess.call(shlex.split("adb shell pm clear %s" % package_title))

    if profile["measure_privacy"]:
        utils.log("Saving runs and its network requests to database")
        run = {}
        run["requests"] = []
        run["run_id"] = run_id
        run["package_title"] = package_title
        while not request_queue.empty():
            serialized_request = request_queue.get()
            run["requests"].append(serialized_request)
        runs.insert(run)

    utils.log("Uninstalling %s" % package_name)
    subprocess.call(shlex.split("adb shell pm uninstall -k %s" % package_title))
