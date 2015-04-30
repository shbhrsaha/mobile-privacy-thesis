
import sys
from random import shuffle

lines = [line for line in sys.stdin]
shuffle(lines)

for line in lines:
    sys.stdout.write(line)
