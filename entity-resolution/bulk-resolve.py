"""
    Resolves domains to company names

    Usage:
        python bulk-resolve.py entity_cache.csv < [domains file]

"""

import sys
import csv
import shlex
import subprocess

domain_lookup = {}

with open(sys.argv[1], 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        domain_lookup[row[0]] = row[1]

counter = 0
for line in sys.stdin:
    line = line.replace("\n", "")
    print line

    if line in domain_lookup:
        continue

    cmd = shlex.split("whois -h geektools.com %s" % line)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    output_lines = out.split("\n")

    for l in output_lines:
        if "Registrant Organization" in l:
            domain_lookup[line] = l.split(":")[-1]

    counter += 1

    if counter % 1 == 0:
        with open(sys.argv[1], 'wb') as f:
            writer = csv.writer(f)
            writer.writerows([(key, value) for key, value in domain_lookup.items()])
