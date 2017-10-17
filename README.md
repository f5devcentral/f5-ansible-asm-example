# f5-ansible-asm-example

## Summary

This project demonstrates deploying WAF via iApps and cloudformation templates. It leverages templates from the official repositories

https://github.com/F5Networks/f5-aws-cloudformation
https://github.com/F5Networks/f5-ansible

Mainly converting the simple deployment approach here  
https://github.com/f5devcentral/f5-aws-autoscale
to using ansible.


## Requirements

Software:

- ansible==2.4.0 
- f5-sdk==3.0.3
- boto==2.46.1
- boto3==1.4.4
- botocore==1.5.30


See included requirements.txt for full environment used.



## Environment Setup

1) Copy and Edit vault.yaml 
 
>cp example-vault.yaml inventory/group_vars/all/vault.yaml 

Edit install_path, passwords, ssh keys, email, etc.


2) update ansible.cfg in top directory to point to latest F5 ansible modules. For instance, the entry "/home/vagrant/git/f5-ansible/library/" in library path: 

```
library=/home/vagrant/git/f5-ansible/library/:./library
```

points to local copy of https://github.com/f5networks/f5-ansible development branch.


Tested with Commit: 4e4a9c94f9ba2d311236509e5dedb27fb1691212


3) If deploying stacks in AWS, configure boto credentials file ~/.aws/credentials

See link below for more detail:
http://boto3.readthedocs.io/en/latest/guide/configuration.html

This user will need permission to create cloudformation stacks with IAM roles.

For more information, see

https://github.com/F5Networks/f5-aws-cloudformation


## Examples

### Deploy New AWS  Stack
```
ansible-playbook -i inventory/hosts playbooks/deploy_aws_stack.yaml -e "deploymentName=demo1 service_name=service1"
```

WARNING: from now on, the playbooks will use dynamic inventory to discover BIG-IP's API host addresses and uses the default host/group naming convention. By default, the cloudformation template will tag the instances with deploymentName. If you use a different deploymentName, you will need to change the playbooks to run on name of that group instead.

ex.
```
cp inventory/group_vars/tag_Name_BIG_IP_Autoscale_Instance__demo1 cp inventory/group_vars/tag_Name_BIG_IP_Autoscale_Instance__\<deploymentName\> 
``

and modify any playbooks to use that group name instead. 


### Onboard - Create REST Username & Password
```
ansible-playbook -i inventory/ec2.py playbooks/onboard_bigip_aws.yaml -e "deploymentName=demo1"
```

### Make a backup File and Upload to S3:
```
ansible-playbook -i inventory/ec2.py playbooks/backup_autoscale_bigip.yaml -e "deploymentName=demo1"
```

### Deploy just an iApp Service on a BIG-IP:
*Uncomment one bigip_iApp_X role you would like to deploy in playbooks/deploy_iApp.yaml. See the description in each role's tasks/main.yaml*

*If you are deploying in AWS, configure the inventory/host_vars/bigip host file to point to your bigip and set the playbooks to run on "hosts: bigips" instead.*


#### bigip_iApp_1 = A simple HTTP service
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=service1"
```

#### bigip_iApp_2 = An advanced HTTPS service with WAF, irules, policies, etc. Requires ASM + AVR to be provisioned.

```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=service1 node_fqdn=www.example.com"

ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=service1 node_fqdn=internal-demo1-AppElb-1373821132.us-west-2.elb.amazonaws.com"
```

#### bigip_iApp_3 = An HTTP service with WAF and fqdn pool
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=demo1 node_fqdn=internal-demo1-AppElb-1373821132.us-west-2.elb.amazonaws.com asm_policy_name=linux-low"

ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=demo1 node_fqdn=internal-demo1-AppElb-1373821132.us-west-2.elb.amazonaws.com asm_policy_name=linux-high"
```

#### bigip_iApp_4 = = An HTTP service with WAF and service discovery iApp for discovering pool members by tags. AWS deployments only.

```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=service1"
```

or setting variables manually

```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=service1 applicationPoolTagKey=aws:autoscaling:groupName applicationPoolTagValue=demo1-application-appAutoscaleGroup-P6D04COZCE1W"
```

#### bigip_iApp_5 = A simple HTTP service using Services iApp:
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=demo1 node_fqdn=internal-demo1-AppElb-1373821132.us-west-2.elb.amazonaws.com"
```


### Deploy Second Service on port 81:

```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=service2 vip_port=81 asm_policy_name=linux-low"
```

##### Update the ASM policy:
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=service2 vip_port=81 asm_policy_name=linux-high"
```


### Deploy an additional service in AWS:
This creates another
 - external LB
 - iApp Service
 - Application in an Auto Scale Group
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_service_aws.yaml -e "deploymentName=demo1 service_name=service2 vip_port=81"
```

##### Teardown additional Service in AWS
```
ansible-playbook -vvvv -i inventory/ec2.py playbooks/teardown_service_aws.yaml -e "deploymentName=demo1 service_name=service2 vip_port=81"
```


### Teardown AWS Stack:
```
ansible-playbook -i inventory/hosts playbooks/teardown_aws_stack.yaml -e "deploymentName=demo1 service_name=service1"
```