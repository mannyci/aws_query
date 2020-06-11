import sys
import logging
from argparse import ArgumentParser

import botocore
from botocore import __version__ as botocore_version

from aws_query import __version__
from aws_query.query import OPSManager
from aws_query.utils.client import get_client
from aws_query.argparser import get_args

logger = logging.getLogger(__name__)

def main():
  c = CLIManager()
  rc = c.main()
  return rc

def _test_creds():
  """Test user's base credentials, check if we can get identity"""
  try:
    get_client('sts').get_caller_identity()
    logger.debug('Found valid credentials')
  except Exception as e:
    logger.error(e)
    sys.exit(0)

def _setup_child_logs():
  """
  Get only warning logs from child modules
  Change this level to info or debug if you want all logs from child modules
  Chnage this only for debugging
  """
  for _ in ("boto3", "botocore", "urllib3"):
    logging.getLogger(_).setLevel(logging.ERROR)


class CLIManager(object):
  def __init__(self, session=None):
    self.session = botocore.session.get_session() if not session else session
    self.session.user_agent_name = 'aws-query'
    self.session.user_agent_version = __version__
    self.session.user_agent_extra = 'botocore/%s' % botocore_version

  def _setup_logs(self):
    _setup_child_logs()
    logger.setLevel(self.loglevel)
    FORMAT = '%(name)-30s - %(levelname)s - %(message)s'
    logging.basicConfig(level=self.loglevel, format=FORMAT)

  def _parse_top_args(self, args):
    self.loglevel = logging.DEBUG if args.debug else logging.ERROR
    self._setup_logs()
    if args.version:
      print(self.session.user_agent())
      sys.exit(0)
    if args.debug:
      logger.debug('Version: {}'.format(self.session.user_agent()))
      logger.debug('Running with arguments: {}'.format(args))
    # _test_creds()

  def main(self):
    """
    :param args: List of arguments
    """
    args = get_args()
    try:
      self._parse_top_args(args)
    except Exception as e:
      logger.debug(e)
      return 255
    operation = OPSManager(args)
    operation.invoke()
