""" Entrypoint module """
from __future__ import print_function
import sys
from aws_resources.cli import main

if __name__ == '__main__':
  sys.exit(main())
