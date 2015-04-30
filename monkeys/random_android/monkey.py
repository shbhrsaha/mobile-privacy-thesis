
import shlex
import subprocess

class Monkey:

    def __init__(self, parameters):
        print "Random Android created"

    def run(self, device, package_title, parameters):
        subprocess.call(shlex.split("adb shell monkey -s 100 -p %s --throttle 500 --pct-touch 75 --pct-motion 25 240" % package_title))