import sys
import logging
from argparse import ArgumentParser


def get_args():
  """Parse arguments from command line"""
  parser = ArgumentParser(
    description=('List AWS resources')
  )

  parser.add_argument("-s", "--service", help="AWS Service(s) to scan for resources. If not specified scans all available AWS services", nargs="+")
  parser.add_argument("-r", "--region", help="AWS Region(s) to scan. If not spefied scans in all available regions for service.", nargs="+")

  parser.add_argument("--account", help="Target AWS account ID, an IAM role name must be specified", type=int)
  parser.add_argument("--role", help="IAM Role to assume on target account. Account ID(s) is required if specified.", type=str)
  parser.add_argument("--profile", help="Use a profile from AWS credential file", type=str)

  parser.add_argument("--all", help="Query all AWS service(s)", action="store_true")
  parser.add_argument("--version", help="Show version", action="store_true")
  parser.add_argument("--debug", help="Enable debug mode", action="store_true")

  if len(sys.argv)==1:
      parser.print_help(sys.stderr)
      sys.exit(1)
  args = parser.parse_args()
  # Check dependent arguments
  required_together = ('role','account')
  if any([getattr(args,_) for _ in required_together]):
    if not all([getattr(args,x) for x in required_together]):
      parser.error('Required arguments --account and --role')
  return(args)



