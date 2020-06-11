import boto3
import botocore
import logging
import sys
from difflib import get_close_matches

logger = logging.getLogger(__name__)

class ServiceManager(object):
  """
  Main class for aws services

  :param services: List of services
  :type services: list
  :param regions: List of regions
  :type regions: list

  """
  def __init__(self, services=None, regions=None):
    self.session = botocore.session.get_session()
    self.services = services or self.get_all_services
    self.regions = regions
    self.queries = []

  def __call__(self):
    return self.services

  def _setup_loader(self):
    if self.services:
      for service in self.services:
        self._check_service(service)
        for region in self._get_service_regions(service):
          # logger.info('{} {}'.format(service, region))
          # TODO build and return a queryset
          self.queries.append([service, region])

  @property
  def get_all_services(self):
    """
    Returns a list of all AWS services

    :rtype list
    """
    return [service for service in self.session.get_available_services()]

  def get_all_queries(self):
    """
    Returns queries to be run
    :rtype: list
    :return: List of queryies to be made
    :format: [['service', 'region']]
    """
    self._setup_loader()
    return self.queries

  def _check_service(self, service):
    if not service in self.get_all_services:
    # TODO - one line
    # if not ([service in boto3.Session().get_available_services() for service in self.services]):
      matches = get_close_matches(service, self.get_all_services)
      logger.error('Invalid service: {}'.format(service))
      if matches:
        logger.info('Maybe you meant: {}'.format(', '.join(_ for _ in matches)))
      logger.debug('Available services: {}'.format(boto3.Session().get_available_services()))
      sys.exit()

  def _get_service_regions(self, service):
    if service in ('iam', 'cloudfront', 's3', 'route53', 'ce'):
      logger.info('{} is a global service, setting region to None'.format(service))
      return [None]
    service_regions = self.session.get_available_regions(service)
    if self.regions:
      for region in self.regions:
        if not region in service_regions:
          logger.error('{} is not available in {}'.format(service, region))
          logger.debug('{} is available in {}'.format(service, service_regions))
          sys.exit()
        else:
          service_regions = self.regions
    logger.debug('Querying in {} region(s) for {}'.format(len(service_regions), service))
    return list(service_regions)
