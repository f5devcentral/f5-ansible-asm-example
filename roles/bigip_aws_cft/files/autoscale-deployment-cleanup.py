#!/usr/bin/python
'''
Simple Python Script to cleanup BIG-IP autoscale solution so can tear down stack
usage:

python bigip-autoscale-cleanup.py --region 'us-east-1' \
                            --aws_access_key XXXXXXXXXXXXX \
                            --aws_secret_key XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
                            --autoscale_group "bigip-BigipAutoscaleGroup-15664Q6QU7C4B" \
                            --s3Bucket "dev-proxy-stack-s3bucket-fsb2vghuyy0i"

'''


import os
import sys
import time
from optparse import OptionParser

#sys.path.insert(0, "/opt/aws")

import botocore
import boto3
import json
import requests
requests.packages.urllib3.disable_warnings()


def main() :
    try:

        print "Autoscale Cleanup Script started"

        parser = OptionParser()
        parser.add_option("-r", "--region", action="store", type="string", dest="region", help="aws region" )
        parser.add_option("-a", "--autoscale_group", action="store", type="string", dest="autoscale_group", help="bigip autoscale group name" )
        parser.add_option("-s", "--s3bucket", action="store", type="string", dest="s3_bucket", help="s3bucket" )
        parser.add_option("--aws_access_key", action="store", type="string", dest="aws_access_key", help="aws_access_key" )
        parser.add_option("--aws_secret_key", action="store", type="string", dest="aws_secret_key", help="aws_secret_key" )
        parser.add_option("-l", "--debug_logging", action="store", type="string", dest="debug_logging", default=False, help="debug logging: True or False" )

        (options, args) = parser.parse_args()

        debug_logging = False
        #setEnvironmentVariables()
        if options.debug_logging == "True":
            debug_logging = True

        # OVERRIDE
        if options.aws_access_key:
            #print "AWS Keys are Passed as Args"
            aws_access_key = options.aws_access_key
            aws_secret_key = options.aws_secret_key
        elif 'AWS_ACCESS_KEY_ID' in os.environ:
            #print "Getting Keys from Environment Vars"
            aws_access_key = os.environ["AWS_ACCESS_KEY_ID"]
            aws_secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
        else:
            aws_access_key = None
            aws_secret_key = None
            if debug_logging == True:
                print "Boto relying on credentials from default ~/.aws/credentials"


        region = options.region
        asg_name = options.autoscale_group
        s3_bucket_name = options.s3_bucket


        if aws_access_key and aws_secret_key:

            # Override boto creds with ones passed in
            # Create ASG client
            try:
                asg_client = boto3.client('autoscaling', region_name=region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key ) # Create Autoscale client
            except botocore.exceptions.ClientError as e:
                print e
                sys.exit("Exiting...")

            # Create EC2 client
            try:
                s3_client = boto3.client('s3', region_name=region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key ) # Create Autoscale client
            except botocore.exceptions.ClientError as e:
                print e
                sys.exit("Exiting...")

        else:
            # Try using ~/.aws/credentials
            # Create ASG client
            try:
                asg_client = boto3.client('autoscaling', region_name=region ) # Create Autoscale client
            except botocore.exceptions.ClientError as e:
                print e
                sys.exit("Exiting...")

            # Create EC2 client
            try:
                s3_client = boto3.client('s3', region_name=region ) # Create Autoscale client
            except botocore.exceptions.ClientError as e:
                print e
                sys.exit("Exiting...")


        #autoscaling = boto3.client('autoscaling')
        #s3_client = boto3.client('s3')
        s3 = boto3.resource('s3')
        ec2 = boto3.resource('ec2')
        instances = []
        asg = ""

        # Removing Scale-In protection from Master 
        for instance in asg_client.describe_auto_scaling_instances()['AutoScalingInstances']:
            if asg_name == instance['AutoScalingGroupName']:
                instances.append( instance['InstanceId'])
                asg = instance['AutoScalingGroupName']
        if instances:
            print 'Auto Scale: Removing Scale-In protection from Master: ',instances
            asg_client.set_instance_protection(
                    InstanceIds = instances,
                    AutoScalingGroupName=asg,
                    ProtectedFromScaleIn=False
                    )
        # Delete S3 Bucket
        buckets = s3_client.list_buckets()['Buckets']
        for bucket in buckets:
            if s3_bucket_name == bucket['Name']:
                print 'S3: deleting S3 bucket: ',bucket['Name']
                b = s3.Bucket(bucket['Name'])
                b.objects.all().delete()
                b.delete()

        print "Autoscale Cleanup Script Finished"

    except Exception, ex:
        print "An exception of type " + type(ex).__name__ + \
            " with message " + str(sys.exc_info()[1])

if __name__ == '__main__':
    main()
