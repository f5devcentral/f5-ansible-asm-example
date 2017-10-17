# f5-ansible-asm-example

## Summary

This project demonstrates deploying WAF via iApps and cloudformation templates. It leverages templates from the official repositories

https://github.com/F5Networks/f5-aws-cloudformation
https://github.com/F5Networks/f5-ansible

Mainly converting the simple deployment approach here  
https://github.com/f5devcentral/f5-aws-autoscale
to using ansible.


## Requirements


ansible==2.4.0 
f5-sdk==3.0.3
boto==2.46.1
boto3==1.4.4
botocore==1.5.30


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


3) If deploying stacks in AWS, edit your credentials file ~/.aws/credentials

See link below for more detail:
http://boto3.readthedocs.io/en/latest/guide/configuration.html


## Examples

### Deploy New AWS  Stack
```
ansible-playbook -i inventory/hosts playbooks/deploy_aws_stack.yaml -e "deploymentName=demo1 service_name=service1"
```

### Onboard - Create REST Username & Password
```
ansible-playbook -i inventory/ec2.py playbooks/onboard_bigip_aws.yaml -e "deploymentName=demo1"
```

### Make a backup File and Upload to S3:
```
ansible-playbook -i inventory/ec2.py playbooks/backup_autoscale_bigip.yaml -e "deploymentName=demo1"
```

### Deploy just an iApp Service on a BIG-IP:
*Uncomment one the bigip_iApp role you would like to deploy in playbooks/deploy_iApp.yaml. See the description in each role's tasks/main.yaml*


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