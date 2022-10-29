import pstats
from pstats import SortKey
import sys

def main():
    p = pstats.Stats(sys.argv[1])
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()


if __name__ == "__main__":
    main()