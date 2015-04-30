"""
    Represents state of search at a particular activity
"""

import md5
import xml.etree.ElementTree as ET
from utils import log
import random

class Activity:

    def __init__(self, dom, activity_name):
        self.dom = dom
        self.topop = []
        self.popped = []

        m = md5.new()
        #m.update(ET.tostring(self.dom))
        m.update(activity_name)
        self.dom_hash = m.hexdigest()

        for node in dom.iter("node"):
            if node.attrib["clickable"] == "true":
                self.topop.append(node)

    def pop_node(self):
        """
            Return the next node that can be clicked
            Randomly picks the next node
        """
        if self.topop:
            index = random.randint(0, len(self.topop) - 1)
            node = self.topop.pop(index)
            self.popped.append(node)
            return node
        return None