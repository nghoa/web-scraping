import time
import sys
from random import randrange

def start_pause():
    for remaining in range(randrange(6), 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r Pause finished \n")


def start():
    for i in range(5):
        start_pause()


if __name__ == '__main__':
    start()