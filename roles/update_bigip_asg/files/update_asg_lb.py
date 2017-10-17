#!/usr/bin/python
'''
Simple Python Script to cleanup BIG-IP autoscale solution so can tear down stack
usage:

python update_asg_lb.py --region 'us-east-1' \
                            --aws_access_key XXXXXXXXXXXXX \
                            --aws_secret_key XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
                            --autoscale_group "bigip-BigipAutoscaleGroup-15664Q6QU7C4B" \
                            --lbs "demo1-service1-AppElb"
                            --action "present"

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

        print "Autoscale Group LB list script started"

        parser = OptionParser()
        parser.add_option("-r", "--region", action="store", type="string", dest="region", help="aws region" )
        parser.add_option("-a", "--autoscale_group", action="store", type="string", dest="autoscale_group", help="bigip autoscale group name" )
        parser.add_option("--lbs", action="store", type="string", dest="lbs", help="LB list" )
        parser.add_option("--action", action="store", type="string", dest="action", help="present or absent" )
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
        lbs = options.lbs
        action = options.action

        attach_ouput = ""
        lb_list=[]

        if options.lbs:
            lb_list = lbs.split(",")

        if aws_access_key and aws_secret_key:

            # Override boto creds with ones passed in
            # Create ASG client
            try:
                asg_client = boto3.client('autoscaling', region_name=region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key ) # Create Autoscale client
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

        if action == "present":
            attach_output = asg_client.attach_load_balancers( 
                                                        AutoScalingGroupName=asg_name,
                                                        LoadBalancerNames=lb_list

                                                     )
            if debug_logging == True:
                print "Autoscale Group LB Output = " + str(attach_output)

        if action == "absent":
            attach_output = asg_client.detach_load_balancers( 
                                                        AutoScalingGroupName=asg_name,
                                                        LoadBalancerNames=lb_list
                                                        )
            if debug_logging == True:
                print "Autoscale Group LB Output = " + str(attach_output)


        asg_output = asg_client.describe_auto_scaling_groups( AutoScalingGroupNames=[asg_name] )
        print "Lb list is " + str(asg_output['AutoScalingGroups'][0]['LoadBalancerNames'])


    except Exception, ex:
        print "An exception of type " + type(ex).__name__ + \
            " with message " + str(sys.exc_info()[1])

if __name__ == '__main__':
    main()
