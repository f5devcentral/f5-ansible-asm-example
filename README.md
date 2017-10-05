# f5-ansible-asm-example



Quick Start:

edit inventory/host_vars/bigip.yaml to point to your BIG-IP:

from inside repo, run:

```
install_path=`pwd`

ansible-playbook -vvvv -i inventory/hosts playbooks/deploy_iApp.yaml -e "env_tag=example_deployment install_path=$install_path"

```

NOTE: Also will need to update ansible.cfg to point to latest F5 ansible modules. For instance, the entry "/home/vagrant/git/f5-ansible/library/" in library path: 

```
library=/home/vagrant/git/f5-ansible/library/:./library
```

points to local copy of https://github.com/f5networks/f5-ansible development branch.



