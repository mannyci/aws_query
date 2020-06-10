import boto3
import logging
import sys
from botocore.exceptions import UnknownServiceError

logger = logging.getLogger(__name__)

_CLIENTS = {}

def get_client(service, region=None, account=None):
    """Returns boto3 clients for given service and region"""
    if (service, region) not in _CLIENTS:
        try:
            _CLIENTS[(service, region)] = boto3.Session(region_name=region).client(service)
        except Exception as e:
            if isinstance(e, UnknownServiceError):
                logger.error('Unknown service {}'.format(service))
            logger.debug(e)
            sys.exit()
    return _CLIENTS[(service, region)]
