"""
    Walks through configuration of privacy research environment
"""

import os
import sys
import yaml
import shlex
import logging
import subprocess

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

def log(message):
    logging.info(message)

def run(command):
    subprocess.call(shlex.split(command))

log("Loading configuration profile")
#with open(sys.argv[1], "r") as f:
#    profile = yaml.load(f.read())
profile = {"mongo_data_dir":"mongodata"}

log("Create MongoDB data directory")
if not os.path.exists(profile["mongo_data_dir"]):
    os.makedirs(profile["mongo_data_dir"])

log("Starting MongoDB (ignore errors)")
run("sudo mongod --fork --syslog --port 27017 --dbpath %s" % profile["mongo_data_dir"])

# OS X only
log("Enabling IP forwarding")
run("sudo sysctl -w net.inet.ip.forwarding=1")

# OS X only
log("Enabling pf.conf")
run("sudo pfctl -f osx/pf_sharing.conf")
run("sudo pfctl -e")

# Linux only
log("Creating iptables")
run("sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080")
run("sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8080")

"""
ip_address = profile["host_ip_address"]
android_ip_address = profile["android_ip_address"]

log("Connecting ADB to Android")
run("adb connect %s" % android_ip_address)

log("Adding default gateway")
run("adb shell \"su -c route add default gw %s dev eth0\"" % ip_address)

log("Browse, then press <Enter> to continue: ")
enter = raw_input("")

log("Adding dummy iptables entry")
run("adb shell \"su -c iptables -t nat -A OUTPUT -o eth0 -p tcp --dport 80 -j DNAT --to %s:80\"" % ip_address)

log("Browse, then press <Enter> to continue: ")
enter = raw_input("")

log("Deleting dummy entry")
run("adb shell \"su -c iptables -D OUTPUT 1 -t nat\"")

log("Adding gateway for second time")
run("adb shell \"su -c route add default gw %s dev eth0\""  % ip_address)
"""

log("Configuration complete.")
