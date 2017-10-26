#!/usr/bin/python
'''
Simple Python Script to tag instance with scale-in protection as master 
usage:

python tag-master.py --region 'us-east-1' \
                            --aws_access_key XXXXXXXXXXXXX \
                            --aws_secret_key XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
                            --autoscale_group "bigip-BigipAutoscaleGroup-15664Q6QU7C4B" 

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

        print "Tag Master Script started"

        parser = OptionParser()
        parser.add_option("-r", "--region", action="store", type="string", dest="region", help="aws region" )
        parser.add_option("-a", "--autoscale_group", action="store", type="string", dest="autoscale_group", help="bigip autoscale group name" )
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
                ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key ) 
            except botocore.exceptions.ClientError as e:
                print e
                sys.exit("Exiting...")

        else:
            # Try using ~/.aws/credentials
            # Create ASG client
            try:
                asg_client = boto3.client('autoscaling', region_name=region ) 
            except botocore.exceptions.ClientError as e:
                print e
                sys.exit("Exiting...")

            # Create EC2 client
            try:
                ec2_client = boto3.client('ec2', region_name=region ) 
            except botocore.exceptions.ClientError as e:
                print e
                sys.exit("Exiting...")


        ec2 = boto3.resource('ec2')
        asg = ""
        master_id = ""
        master_tag_value = ""

        # Removing Scale-In protection from Master 
        for instance in asg_client.describe_auto_scaling_instances()['AutoScalingInstances']:
            if asg_name == instance['AutoScalingGroupName'] and instance['ProtectedFromScaleIn'] == True:
                master_id = instance['InstanceId']
                asg = instance['AutoScalingGroupName']
        if master_id:
            response = ec2_client.describe_tags(
                Filters=[
                    {
                        'Name': 'resource-id',
                        'Values': [
                            master_id ,
                        ],
                    },
                ],
            )

            for tag in response['Tags']:
                if tag['Key'] == "Name":
                    master_tag_value = tag['Value']

            if "-master" not in master_tag_value:
                print "Setting Tag for Master ID:" + master_id
                # #"BIG-IP Autoscale Instance: demo1-master"


                ec2_client.create_tags(
                    Resources=[master_id],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': master_tag_value + '-master'
                        }
                    ]
                )

                print "SUCCESS. Tag Master Script Finished"
        else:
            print "FAIL. No master found. exiting"
            sys.exit(1)

    except Exception, ex:
        print "An exception of type " + type(ex).__name__ + \
            " with message " + str(sys.exc_info()[1])

if __name__ == '__main__':
    main()
