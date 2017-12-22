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
- boto==2.46.1
- boto3==1.4.4
- botocore==1.5.30


Latest development branch of the F5 SDK:
pip install --upgrade git+https://github.com/F5Networks/f5-common-python.git


See included requirements.txt for full environment used.



## Environment Setup

1) Copy and Edit Inventory Variables 
 
>cp example-vault.yaml inventory/group_vars/all/vault.yaml 

Edit install_path, passwords, ssh keys, email, etc.

Edit any non secret variables in inventory/group_vars/all/vars.yaml

Edit inventory/hosts to point to your interpreter

```
localhost ansible_python_interpreter=/home/vagrant/ansible-venv/bin/python
```

2) update ansible.cfg in top directory to point to latest F5 ansible modules. 

For instance, the entry "/home/vagrant/git/f5-ansible/library/" in library path: 

```
library=/home/vagrant/git/f5-ansible/library/:./library
```

points to local copy of https://github.com/f5networks/f5-ansible development branch.


Tested with Commit: 
6c2aeaabef33d795c03db7ecdd9b5e82eca91296
(Wed Dec 20 14:56:44 2017 -0800)


3) If deploying stacks in AWS, configure boto credentials file ~/.aws/credentials

See link below for more detail:
http://boto3.readthedocs.io/en/latest/guide/configuration.html

This user will need permission to create cloudformation stacks with IAM roles.

For more information, see

https://github.com/F5Networks/f5-aws-cloudformation


## Examples

### Deploy New AWS  Stack
```
ansible-playbook -i inventory/hosts playbooks/deploy_aws_stack.yaml -e "deploymentName=demo1 service_name=demo1"
```

### Tag Instance as master

```
ansible-playbook -i inventory/hosts playbooks/tag_master_bigip_aws.yaml -e "deploymentName=demo1"
```

WARNING: from now on, the playbooks will use dynamic inventory to discover the BIG-IP's API address and uses the default naming convention. By default, the cloudformation template will tag the instances with the convention

Name:   BIG-IP Autoscale Instance <deploymentName>

We use this playbook to add "-master" to that tag so Ansible's dynamic inventory will create dynamic group with name:

tag_Name_BIG_IP_Autoscale_Instance__{{deploymentName}}_master

which only contains the host IP of the instance with "Scale-In Protection". This is the most reliable host to automate against as it doesn't have a risk of being terminated mid transaction.


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
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=demo1"
```

#### bigip_iApp_2 = An advanced HTTPS service with WAF, irules, policies, etc. 
*Warning: Requires AVR + ASM to be provisioned*

```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=demo1 node_fqdn=www.example.com"
```

#### bigip_iApp_3 = An HTTP service with WAF and fqdn pool
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=demo1 node_fqdn=www.example.com asm_policy_name=linux-low"
```

#### bigip_iApp_4 = = An HTTP service with WAF and service discovery iApp for discovering pool members by tags. AWS deployments only.
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=demo1 applicationPoolTagKey=aws:autoscaling:groupName applicationPoolTagValue=demo1-demo1-application-appAutoscaleGroup-1WL86R38ZV303"
```

#### bigip_iApp_5 = A simple HTTP service using Services iApp
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=demo1 node_fqdn=www.example.com"
```

#### bigip_iApp_6 = An advanced HTTP service with WAF and fqdn member using Services iApp
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=demo1 node_fqdn=www.example.com"
```

### Deploy Second Service on port 81:

```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=service2 vs_port=81 asm_policy_name=linux-low"
```

##### Update the ASM policy:
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_iApp.yaml -e "deploymentName=demo1 service_name=service2 vs_port=81 asm_policy_name=linux-high"
```


### Deploy an additional service in AWS:
This creates another
 - external LB
 - iApp Service
 - Application in an Auto Scale Group
```
ansible-playbook -v -i inventory/ec2.py playbooks/deploy_service_aws.yaml -e "deploymentName=demo1 service_name=service2 vs_port=81"
```

##### Teardown additional Service in AWS
```
ansible-playbook -vvvv -i inventory/ec2.py playbooks/teardown_service_aws.yaml -e "deploymentName=demo1 service_name=service2 vs_port=81"
```

###

Test WAF:
```
curl -H "Content-Type: application/json; ls /usr/bin" http://35.167.82.48/
```


### Teardown AWS Stack:
```
ansible-playbook -i inventory/hosts playbooks/teardown_aws_stack.yaml -e "deploymentName=demo1 service_name=demo1"
```