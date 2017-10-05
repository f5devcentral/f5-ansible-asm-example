# f5-ansible-asm-example



Quick Start:

edit inventory/host_vars/bigip.yaml to point to your BIG-IP:

from inside repo, run:

```
install_path=`pwd`

ansible-playbook -vvvv -i inventory/hosts playbooks/deploy_iApp.yaml -e "env_tag=example_deployment install_path=$install_path"

```
