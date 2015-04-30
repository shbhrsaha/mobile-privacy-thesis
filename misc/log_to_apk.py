"""
    Hackish script that turns a apk-downloader log file into an apks.txt
"""

import sys

log_file = sys.argv[1]
apk_file = sys.argv[2]

package_names = [x.replace("\n","") for x in open(log_file).readlines() if "." in x]
apks = [x+".apk" for x in package_names]

with open(apk_file, "w") as f:
    f.write("\n".join(apks))
