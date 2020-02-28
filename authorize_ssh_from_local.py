#!/usr/bin/env python3

# Documentation for boto3 calls:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.authorize_security_group_egress
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.authorize_security_group_ingress

import argparse
import boto3
import getpass
import logging
import requests
import socket
import settings


logger = logging.getLogger(__name__)


def get_local_ip_address() -> str:
    return requests.get("https://api.ipify.org").text


def flash_security_group(sg: str):
    logger.info(f"flash_security_group: sgroup:{sg}")
    client = boto3.client('ec2')
    security_group = client.describe_security_groups(
        GroupIds=(sg,),
    )
    logger.info(f"describe_security_groups: {security_group}")
    try:
        ciderip = security_group['SecurityGroups'][0]['IpPermissions'][0]['IpRanges'][0]['CidrIp']
    except IndexError as identifier:
        logger.warn(f"No ingress rules to revoke")
        return
    ret = client.revoke_security_group_ingress(
        CidrIp=ciderip,
        FromPort=22,
        GroupId=sg,
        IpProtocol='tcp',
        ToPort=22,
    )
    logger.info(f"revoke_security_group_ingress: {ret}")


def update_security_group(sg: str):
    logger.info(f"update_security_group: sgroup:{sg}")
    client = boto3.client('ec2')
    ret = client.authorize_security_group_ingress(
        GroupId=sg,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'IpRanges': [{
                'CidrIp': get_local_ip_address() + "/32",
                'Description': getpass.getuser() + '@' + socket.gethostname(),
            }],
            'FromPort': 22,
            'ToPort': 22,
        }]
    )
    logger.info(f"authorize_security_group_ingress: {ret}")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Open ssh ingress from the local machine via the supplied security group id.",
    )
    parser.add_argument(
        '--sg',
        default=settings.DEFAULT_SG,
        help="Security Group in the form 'sg-' followed by a long hexidecimal number, e.g., sg-0123456789abcdef",
        type=str,
    )

    args = parser.parse_args()

    flash_security_group(args.sg)
    update_security_group(args.sg)

    exit(0)
