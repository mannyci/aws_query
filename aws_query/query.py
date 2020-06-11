from __future__ import print_function
import boto3
import botocore
import json
import sys
import contextlib
import logging
from collections import defaultdict
from functools import partial
from multiprocessing.pool import ThreadPool

from aws_query.request import RequestMgr
from aws_query.utils.client import get_client
from aws_query.utils.service import ServiceManager
from aws_query.utils.operations import BuildOperation

logger = logging.getLogger(__name__)
class OPSManager(object):
  """Operation manager for the cli.

  :params :args prased arguments
  """
  def __init__(self, args=None, session=None):
    self.args = args
    self.session = session
    self.services = args.service
    self.regions = args.region

  def __call__(self):
    self._load_session()
    self._load_queries()
    self._load_operations()
    self._run_op()

  def invoke(self):
    self._load_session()
    self._load_queries()
    self._load_operations()
    self._run_op()

  def _check_session(self):
    try:
      sts = self.session.create_client('sts')
      id = sts.get_caller_identity()
      logger.info('Session created to {} with {}'.format(id['Account'], id['Arn']))
    except Exception as e:
      logger.error(e)
      sys.exit(255)

  def _base_session(self):
    """
    Get a base session
    """
    self.session = self.session if self.session else botocore.session.get_session()
    if self.args.profile:
      try:
        self.session.set_config_variable('profile', self.args.profile)
      except Exception as e:
        logger.error(e)

  def _load_session(self):
    """
    Setup session based on args, intialized on load.
    We do all session loading here
    """
    self._base_session()
    if self.args.role:
      logger.info('Creating session from {} with {} role'.format(self.args.account, self.args.role))
      roleArn = 'arn:aws:iam::{}:role/{}'.format(self.args.account, self.args.role)
      sts_client = self.session.create_client('sts')
      try:
        assumed_role = sts_client.assume_role(RoleArn=roleArn, RoleSessionName='aws-query')
        credential = assumed_role['Credentials']
        logger.info('Successfully assumed role: {}'.format(roleArn))
        self.session.set_credentials(
          credential['AccessKeyId'],
          credential['SecretAccessKey'],
          credential['SessionToken']
        )
      except Exception as e:
        logger.error('Unable to assume RoleArn: {}'.format(roleArn))
        logger.exception(e)
        sys.exit(255)
    self._check_session()

  def _load_queries(self):
    manager = ServiceManager(services=self.services, regions=self.regions)
    self.queries = manager.get_all_queries()
    logger.debug('{} queries to be made for {} in {}'.format(len(self.queries), manager.services, manager.regions))

  def _load_operations(self):
    self.operations = BuildOperation(self.queries).get_operations()

  def _run_op(self):
    res = RequestMgr(session=self.session, operations=self.operations)
    res()


