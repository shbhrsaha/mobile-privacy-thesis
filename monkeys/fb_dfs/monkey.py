"""
    Completes FB login, if exists, then performs DFS
    Returns after timeout
"""

import shlex
import time
import multiprocessing
import subprocess
import xml.etree.ElementTree as ET
from utils import log
from activity import Activity

class Monkey:

    def __init__(self, parameters):
        log("FB-DFS monkey created")

    def start_package(self):
        subprocess.call(shlex.split("adb shell monkey -p %s -c android.intent.category.LAUNCHER 1" % self.package_title))
        self.device.wait.idle()
        time.sleep(8)

    def run(self, device, package_title, parameters):
        self.device = device
        self.package_title = package_title
        self.parameters = parameters

        p = multiprocessing.Process(target=self._run_process)
        p.start()

        p.join(parameters["timeout"])

        if p.is_alive():
            log("Timeout complete. Returning")
            p.terminate()
            p.join()

        return

    def _run_process(self):
        log("Starting %s" % self.package_title)
        self.start_package()

        log("Logging into FB, if possible")
        if self.try_signin_with_facebook():
            log("Waiting 10 seconds before starting DFS")
            time.sleep(10)

        log("Starting DFS exploration")
        self.activity_hashes = {}
        self.dfs_explore()

    def try_signin_with_facebook(self, stop=False):
        """
            Searches for a Facebook button and logs in if found

            stop=True ends the recursive search
        """
        log("Deconstructing UI")
        xml = self.device.dump()
        dom = ET.fromstring(xml.encode('utf-8'))

        log("Searching for Facebook login button")
        button_fb = self.get_facebook_login_button(dom)
        if button_fb is None:
            log("Facebook button not found. Searching for signin/signup button")
            button_auth = self.get_auth_button(dom)

            if button_auth is not None and not stop:
                log("Signin/signup button found. Clicking")
                self.device(text=button_auth.attrib["text"], className=button_auth.attrib["class"]).click()
                self.device.wait.idle()
                return self.try_signin_with_facebook(stop = True)

            log("Signin/signup button not found. Exiting Facebook login sequence")
            return None

        log("Facebook button found. Proceeding with login")
        try:
            self.device(text=button_fb.attrib["text"], className=button_fb.attrib["class"]).click()
        except:
            log("False positive for Facebook button. Closing Facebook login sequence")
            return None
        self.device.wait.idle()

        log("Verifying Facebook is current activity")
        time.sleep(3)
        current_activity = self.get_current_activity()
        if self.parameters["facebook_app_code"] not in current_activity:
            log("Did not detect Facebook activity")

            if self.package_title in current_activity:
                log("But package is still running. Exiting Facebook login sequence")
                return True

            log("Package is not running. Restarting and exiting Facebook login sequence")
            self.start_package()
            return True

        log("Current activity is Facebook verification successful. Clicking through permissions sequence")
        while self.parameters["facebook_app_code"] in self.get_current_activity():
            """
            time.sleep(1)
            self.device.press("right")
            time.sleep(1)
            self.device.press("right")
            time.sleep(1)
            self.device.press("enter")
            self.device.wait.idle()
            time.sleep(3)
            """
            time.sleep(1)
            self.device.click(1000,1700)
            time.sleep(3)
            if self.parameters["facebook_app_code"] in self.get_current_activity():
                self.device.click(1700,1000)

        if self.package_title in self.get_current_activity():
            log("Permissions sequence successful. Returned to original package")
            return True

        log("Something went wrong during permissions sequence. Restarting and exiting Facebook login sequence")
        self.start_package()
        return True

    def get_auth_button(self, dom):
        """Returns the sign in/sign up button or None if not found"""

        # sign up
        for node in dom.iter('node'):
            text = node.attrib["text"].lower()
            if "sign" in text and "up" in text and node.attrib["clickable"]:
                return node

        # sign in
        for node in dom.iter('node'):
            text = node.attrib["text"].lower()
            if (("sign" in text and "up" in text) or ("log" in text and "in" in text)) and node.attrib["clickable"]:
                return node

        return None

    def get_facebook_login_button(self, dom):
        """Returns the Facebook login button or None if not found"""
        for node in dom.iter('node'):
            if "Facebook" in node.attrib["text"] and node.attrib["clickable"]:
                return node

        return None

    def dfs_explore(self, last_dom_hash=None):
        self.device.wait.idle()
        time.sleep(5)
        log("Identifying current activity")
        activity = self.get_activity()

        if not self.app_is_active():
            log("App is not active. Restarting app")
            self.start_package()
            return

        if activity.dom_hash == last_dom_hash:
            log("Activity didn't change. Moving onto next node")
            return

        if activity.dom_hash in self.activity_hashes:
            log("Seen this activity before. Going back")
            self.device.wait.idle()
            self.device.press.back()
            self.device.wait.idle()
            return

        self.activity_hashes[activity.dom_hash] = None

        node = activity.pop_node()
        while node is not None:

            # TODO: this is a hack because clicking back doesn't always
            # bring you back to the activity you'd expect, so somehow
            # we have to deal with that
            # verify that activity hasn't changed in this loop iteration
            potentially_new_activity = self.get_activity()
            if activity.dom_hash != potentially_new_activity.dom_hash:
                self.dfs_explore()
                return

            log("Clicking node index %s" % node.attrib["index"])
            try:
                self.device(index=node.attrib["index"]).click()
                self.device.wait.idle()
            except:
                log("Failed to click. Moving on")
                pass
            self.dfs_explore(last_dom_hash=activity.dom_hash)
            node = activity.pop_node()

        return

    def get_activity(self):
        return Activity(self.get_dom(), self.get_current_activity())

    def get_dom(self):
        xml = self.device.dump()
        return ET.fromstring(xml.encode('utf-8'))

    def get_current_activity(self):
        """Returns the currently running activity"""
        cmd = shlex.split("adb shell dumpsys window windows | grep -E 'mCurrentFocus'")
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        activity_name = out.split("\n")[0]

        if "Application Error" in activity_name:
            self.device(text="OK").click()
            return self.get_current_activity()

        return activity_name

    def app_is_active(self):
        return self.package_title in self.get_current_activity()
