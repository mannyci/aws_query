import sys
import contextlib
import logging
from collections import defaultdict
from functools import partial
from multiprocessing.pool import ThreadPool

from aws_resources.utils.client import get_client

logger = logging.getLogger(__name__)

_ACTION = ['Describe', 'Get', 'List']

class BuildOperation(object):
  """
  Operation builder for based on action strings

  :param :queries: List of service and region e.g. [['service', 'region']]
  :type :queries: list

  """
  def __init__(self, queries=None):
    self.queries = queries
    self.operations = []

  def _build_operations(self):
    with contextlib.closing(ThreadPool(25)) as pool:
      pool.map(partial(self._get_operations), self.queries)

  def _get_operations(self, query):
    service, region = query
    client = get_client(service, region)
    logger.debug('Getting operations for {} in {}'.format(service, region))
    for operation in client.meta.service_model.operation_names:
      if not any(operation.startswith(prefix) for prefix in _ACTION):
        continue
      op_model = client.meta.service_model.operation_model(operation)
      required_members = op_model.input_shape.required_members if op_model.input_shape else []
      required_members = [m for m in required_members if m != 'MaxResults']
      if required_members:
        continue
      self.operations.append([service, region, operation])

  def get_operations(self):
    """
    Returns list of queries

    :rtype :List
    """
    self._build_operations()
    return self.operations

