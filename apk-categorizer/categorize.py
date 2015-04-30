"""
    Categorizes APKs into their Google Play store category

    Usage:
        python categorize.py [database CSV file] [APKs to process file]

"""

import sys
import csv
from pattern.web import URL, DOM, plaintext


package_categories = {}

with open(sys.argv[1], 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        package_categories[row[0]] = row[1]

package_titles = [x.replace(".apk","").replace("\n","") for x in open(sys.argv[2]).readlines()]

counter = 0
for package_title in package_titles:
    if package_title in package_categories:
        continue

    try:
        url = URL("https://play.google.com/store/apps/details?id=%s" % package_title)
        dom = DOM(url.download(cached=True))
        for e in dom('a.category'):
            category = e.href.split("/")[-1]
            package_categories[package_title] = category
    except:
        print "Request failed on %s" % package_title
        pass

    counter += 1

    if counter % 5 == 0:
        with open(sys.argv[1], 'wb') as f:
            writer = csv.writer(f)
            writer.writerows([(key, value) for key, value in package_categories.items()])
        print counter

