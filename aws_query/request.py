import sys
import pprint
import json
from datetime import datetime
import logging
import botocore
import contextlib
from collections import defaultdict
from functools import partial
from multiprocessing.pool import ThreadPool
from botocore.exceptions import UnknownServiceError

_CLIENTS = {}
logger = logging.getLogger(__name__)


class RequestMgr(object):
  """
  Class for making an api call to AWS. We get a list of operations and a session.
  """
  def __init__(self, session=None, operations=None):
    self.session = session
    self.operations = operations

  def __call__(self):
    self._make_thread()

  def _get_client(self, service=None, region=None):
    """
    Returns botocore client from session
    """
    if (service, region) not in _CLIENTS:
      try:
        _CLIENTS[(service, region)] = self.session.create_client(service, region_name=region)
      except Exception as e:
        if isinstance(e, UnknownServiceError):
          logger.error('Unknown service {}'.format(service))
        logger.debug(e)
        sys.exit()
    return _CLIENTS[(service, region)]

  def _make_thread(self):
    with contextlib.closing(ThreadPool(25)) as pool:
      pool.map(partial(self._make_request), self.operations)

  def _make_request(self, op):
    service, region, operation = op
    client = self._get_client(service=service, region=region)
    try:
      res = ResManager.run_operation(client=client, operation=operation)
      if res.total_count > 0:
        print(res)
        json_data = {
          'service': service,
          'region': region,
          'data': res.parsed_resources,
        }
        with open('{}.json'.format(service), 'w') as outfile:
          json.dump(json_data, outfile, default=datetime.isoformat)
    except Exception as e:
      logger.debug('Exception on service {} in {} {}: {}'.format(service, region, operation, e))

class ResManager(object):
  def __init__(self, client=None, operation=None, response=None):
    self.client = client
    self.operation = operation
    self.response = response

  def __str__(self):
    desc = '{}'.format(self.operation)
    for key, listing in self.parsed_resources.items():
      if isinstance(listing, list):
        return desc + ', '.join(' # {}: {}'.format(key, len(listing)) for key, listing in self.parsed_resources.items())
      else:
        return desc + ', '.join(' # {}: {}'.format(key, listing) for key, listing in self.parsed_resources.items())

  @property
  def get_response(self):
    return self.parsed_resources

  @classmethod
  def run_operation(cls, client=None, operation=None):
    api_to_method_mapping = dict((value, key) for key, value in client.meta.method_to_api_mapping.items())
    r = getattr(client, api_to_method_mapping[operation])()
    return cls(client=client, operation=operation, response=r)

  @property
  def total_count(self):
    """The estimated total count of resources - can be incomplete"""
    return sum(len(v) for v in self.parsed_resources.values())

  @property
  def parsed_resources(self):
    """Process the response data"""
    response = self.response.copy()
    del response['ResponseMetadata']

    # Owner Info is not necessary
    if self.operation == 'ListBuckets':
      del response['Owner']
    return response


