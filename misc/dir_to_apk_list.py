"""
    Creates an apk list from the list of files in a directory

    Usage:
        python dir_to_apk_list.py [directory] [apk list file]
        python dir_to_apk_list.py ../apk-downloader/ ../apk-downloader/apks.txt
"""

import os
import sys

files = os.listdir(sys.argv[1])
apklistfile = sys.argv[2]
towrite = []

for apkfile in files:
    if apkfile[-4:] == ".apk":
        towrite.append(apkfile)

with open(apklistfile, "w") as f:
    f.write("\n".join(towrite))