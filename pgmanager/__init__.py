import os
import sys
from fabric import main as main_fabric
from fabfile import *

__version__ = '0.0.1'

sys.argv.append('-f')
sys.argv.append('pgmanager_fabfile.py')
sys.path.append(os.getcwd())


def main():
    main_fabric.main()


if __name__ == "__main__":
    main()
