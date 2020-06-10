from aws_resources.utils.client import get_client
import boto3
import botocore
import logging


logging.getLogger('boto3').setLevel(logging.DEBUG)

sts = get_client('sts')
account = sts.get_caller_identity()
del account['ResponseMetadata']
# print(account)

roleARN = 'arn:aws:iam::{}:role/{}'.format('843543910397', 'test_assume')
a = sts.assume_role(RoleArn=roleARN, RoleSessionName='test-role')
cred = a['Credentials']


s = botocore.session.get_session()
s.set_credentials(cred['AccessKeyId'], cred['SecretAccessKey'], cred['SessionToken'])
t = s.create_client('sts')
print(t.get_caller_identity())

# tmp = boto3.Session(botocore_session=s).client('sts')
# print(tmp.get_caller_identity())

class Test(object):
  def __init__(self, obj, *args):
    print(obj.session)
    print(*args)
    self.session = botocore.session.get_session() if not session else session
    self.session.user_agent_name = 'bla'
    self.sts = self.session.create_client('sts')
    self.id = self.sts.get_caller_identity()
    print(self.id)

  @classmethod
  def main(cls, args=None, session=None):
    return cls()

class Bla(object):
  def __init__(self):
    self.session = s
    print(s.get_credentials().access_key)
    test = Test(self)

Bla()