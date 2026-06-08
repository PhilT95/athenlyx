![Ansible Banner](images/ansible_logo.png)

# Ansible - Automation and Infrastructure as Code

Ansible is a collection of software tools used to automate infrastructure management. Generally know as IaC, it can cover:

1. Software provisioning
2. Configuration management
3. Application deployment



## Basics of Ansible

The ansible software connects to different hosts, which can be other servers, network devices or even clients, to deploy and execute small programs. These programs are then used to automate tasks on the targeted hosts to transform the target into a desired state. Once Ansible executed these programs they are removed. Enabling Ansible requires at least the following components:

|Component|Description|
|:--------|:----------|
|**Inventory**|The ansible inventory resembles the infrastructure inventory and contains all servers that should be managed by Ansible. These are ansible-specific text files which contain their host names or IP-Addresses.|
|**Playbook**|An Ansible Playbook is an ordered list of instructions and programs that are executed on the targeted hosts. The playbooks are .yml files.|
|**Authentication**|Ansible requires a way to authenticate with the hosts. This usually can be done using **SSH** and a dedicated ansible user that needs to be provided on the targets.|

Once all these components are setup Ansible can connect to the machines that are named inside the inventory file(s) and using the playbook and the ansible binary, the programs that are listed inside the playbook can be executed on the targets.

!!! info
    Ansible usually connects using the user that is currently executing the command. Therefore, the dedicated Ansible user should also exist on the Ansible server and execute the command itself. This user should exist on all managed devices that are to be managed by Ansible.

