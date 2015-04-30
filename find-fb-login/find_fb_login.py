"""
    Prints to stdout the package names that use the Facebook API

    Must run in apk-decompiler directory:
        python find_fb_login.py ../profiles/find_fb_login.yml
"""

import os
import sys
import subprocess
import shlex
import yaml
import logging

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

def log(message):
    logging.info(message)

log("Loading profile")
with open(sys.argv[1], "r") as f:
    profile = yaml.load(f.read())

log("Loading APK file list")
with open(profile["apk_list"]) as f:
    apk_filenames = [x.replace("\n","") for x in f.readlines()]

log("Loading cache")
with open("hasfb.txt") as f:
    apk_hasfb = [x.replace("\n","") for x in f.readlines()]
with open("nofb.txt") as f:
    apk_nofb = [x.replace("\n","") for x in f.readlines()]

counter = 0
for apkname in apk_filenames:
    if apkname in apk_hasfb or apkname in apk_nofb:
        log("%s already in cache. Continuing" % apkname)
        continue

    log("Decompiling #%s %s" % (counter, apkname))
    apkfile = profile["apk_dir"]+"/"+apkname

    os.system("rm manifest.log")
    os.system("aapt l -a %s > manifest.log" % apkfile)
    manifest_content = open("manifest.log","r").read()

    if "com.facebook.sdk.ApplicationId" in manifest_content:
        log("%s has FB SDK. Saving" % apkname)
        apk_hasfb.append(apkname)
    else:
        log("%s does not have FB SDK. Saving" % apkname)
        apk_nofb.append(apkname)

    if counter % 10 == 0:
        with open("hasfb.txt", 'w') as f:
            f.write("\n".join(apk_hasfb))
        with open("nofb.txt", 'w') as f:
            f.write("\n".join(apk_nofb))

    counter += 1

with open("hasfb.txt", 'w') as f:
    f.write("\n".join(apk_hasfb))
with open("nofb.txt", 'w') as f:
    f.write("\n".join(apk_nofb))