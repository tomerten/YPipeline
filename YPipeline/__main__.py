import sys

from . import log

if __name__ == "__main__":
    log.setup()

    n = int(sys.argv[1])

    log.info(n)
