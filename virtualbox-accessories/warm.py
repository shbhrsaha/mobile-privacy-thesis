"""
    Keeps Android from falling asleep (warm!)
    by tapping every five seconds

    Usage:
        python warm.py [adb device id]
"""

import sys
import os
import time
from uiautomator import Device

DEVICE_NAME = sys.argv[1]
d = Device(DEVICE_NAME)

d.wakeup()

os.system("adb shell content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:0")

while True:
    d.click(100, 100)
    time.sleep(5)
