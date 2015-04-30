"""
    Records mouse clicks in the context of blob extraction

    Usage:
        python record.py [virtual machine name] [folder to save images in]

"""

import subprocess
import shlex
import sys
import virtualbox

from skimage import data, io, morphology, measure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from skimage.filter import sobel, gaussian_filter
from skimage.feature import blob_doh
from skimage.color import rgb2gray
from skimage.feature import CENSURE
import numpy as np

from SimpleCV import *

MACHINE_NAME = sys.argv[1]
SAVE_FOLDER = sys.argv[2]

counter = 0

def record_mouse(event):
    """
    Save a mouse action
    """
    global counter
    global session

    if event.buttons != 1:
        return

    h, w, _, _, _ = session.console.display.get_screen_resolution(0)
    png = session.console.display.take_screen_shot_png_to_array(0, h, w)

    with open('screenshot.png', 'wb') as f:
        f.write(png)

    IMAGE_FILE_PATH = "screenshot.png"
    FILE_TO_SAVE = "%s%s.png" % (SAVE_FOLDER, counter)

    # load image
    image = data.imread(IMAGE_FILE_PATH)
    image = rgb2gray(image)

    # edges
    image = sobel(image)

    # blur
    image = gaussian_filter(image, sigma=10)

    mpimg.imsave("output.png", image)

    img = Image("output.png")
    img_original = Image(IMAGE_FILE_PATH)
    image = Image(IMAGE_FILE_PATH)
    blobs = img.findBlobs(threshval = -1, minsize=10, maxsize=0, threshblocksize=0, threshconstant=5, appx_level=3)
    if blobs:
        blobs.draw(width=10)
    img.save(FILE_TO_SAVE)
    img_original.save(FILE_TO_SAVE+"_original.png")

    counter += 1

print "Connecting to virtual machine"

try:
    vbox = virtualbox.VirtualBox()
    vm = vbox.find_machine(MACHINE_NAME)
    session = vm.create_session()
except:
    raise Exception("Could not find virtual machine %s. Please make sure it exists." % args.vm_name)

print "Hello"

print "Registering to receive keyboard and mouse events"
session.console.mouse.register_on_guest_mouse(record_mouse)

print "Recording... Press <ENTER> to stop."
stop = raw_input()