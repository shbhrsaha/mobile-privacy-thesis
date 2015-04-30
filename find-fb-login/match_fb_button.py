"""
    Prints to stdout the package names that use the Facebook API

    Similar to find_fb_login, but actually filters it down further
    by decompiling and searching for "with Facebook" phrase in code
"""

import os
import sys
import subprocess
import shlex
import yaml
import logging

logging.basicConfig(format='%(message)s', level=logging.DEBUG, filename='../runs.log')

def log(message):
    logging.info(message)

log("Loading profile")
with open(sys.argv[1], "r") as f:
    profile = yaml.load(f.read())

log("Loading APK file list")
with open(profile["apk_list"]) as f:
    apk_filenames = [x.replace("\n","") for x in f.readlines()]

log("Loading cache")
with open("hasfbbutton.txt") as f:
    apk_hasfb = [x.replace("\n","") for x in f.readlines()]
with open("nofbbutton.txt") as f:
    apk_nofb = [x.replace("\n","") for x in f.readlines()]

counter = 0
for apkname in apk_filenames:
    try:
        if apkname in apk_hasfb or apkname in apk_nofb:
            log("%s already in cache. Continuing" % apkname)
            counter += 1
            continue

        log("Decompiling #%s %s" % (counter, apkname))
        apkfile = profile["apk_dir"]+"/"+apkname

        subprocess.check_output(
            ['rm', '-rf', 'temp'], stderr=subprocess.STDOUT
        )

        subprocess.check_output(
            ['unzip', apkfile, '-d', 'temp'], stderr=subprocess.STDOUT
        )

        p = subprocess.Popen(shlex.split('grep "with Facebook" -R temp'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if out:
            apk_hasfb.append(apkname)
        else:
            apk_nofb.append(apkname)

        if counter % 10 == 0:
            with open("hasfbbutton.txt", 'w') as f:
                f.write("\n".join(apk_hasfb))
            with open("nofbbutton.txt", 'w') as f:
                f.write("\n".join(apk_nofb))
    except:
        apk_nofb.append(apkname)
        continue

    counter += 1

with open("hasfbbutton.txt", 'w') as f:
    f.write("\n".join(apk_hasfb))
with open("nofbbutton.txt", 'w') as f:
    f.write("\n".join(apk_nofb))
