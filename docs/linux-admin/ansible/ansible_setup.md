# Ansible Setup Guide for AlmaLinux 10

This guide will provide step-by-step instructions and necessary commands to install Ansible and get a basic configuration ready on AlmaLinux 10.

## Requirements

To continue with the following guide please make sure that your setup meets the following requirements:

- A AlmaLinux 10 instance with internet access
- SSH & root access to this AlmaLinux machine
- Network & SSH access to at least one other system from the instance
- Root access to this other system

## Setup

### Installing Ansible

This part of the setup is pretty straight-forward. Connect to your AlmaLinux 10 instance where you want to install Ansible using SSH. Once you are connected you will need root access so we can update and install ansible.

```console
[admin@ansible ~]$ sudo su
[root@ansible ~]# dnf upgrade -y
[root@ansible ~]# dnf install ansible-core -y
```

Verify the ansible installation and version using the `ansible --version` command.

```console
[root@ansible ~]# ansible --version
ansible [core 2.16.16]
  config file = /etc/ansible/ansible.cfg
  configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python3.12/site-packages/ansible
  ansible collection location = /root/.ansible/collections:/usr/share/ansible/collections
  executable location = /bin/ansible
  python version = 3.12.13 (main, Apr 16 2026, 00:00:00) [GCC 14.3.1 20251022 (Red Hat 14.3.1-4)] (/usr/bin/python3)
  jinja version = 3.1.6
  libyaml = True
```

This command also reveals the location of the ansible configuration files, including the default playbook & inventory files under `/etc/ansible/`.

Finally, using **Ansible Galaxy**, the collection that enables ansible to handle *dnf* packages needs to be installed.

```console
[root@ansible ~] ansible-galaxy collection install community.general
```

### Ansible user setup

Since Ansible usually connects to different systems and therefore is a bigger security risk within a network, extra steps need to be taken to make malicious actions more difficult. One important step to reduce the risk is using a separate and dedicated Ansible user, which on the Ansible system itself has as few permissions as possible. 

To start, the user needs to be created and a password should be set. You will be asked to enter and confirm the password for the new user *ansible*.

```console
[root@ansible ~]# useradd ansible
[root@ansible ~]# passwd ansible
```

We also create a new group to make the management of permission independent of the user and add the user to the group.

```console
[root@ansible ~]# groupadd g-ansible
[root@ansible ~]# usermod -aG g-ansible ansible
```

Once the user and the group is created we need to give the members of the group necessary permissions to edit the ansible configuration files. The easiest way to do this is using the tool `setfacl`, which based on group memberships allows you to assign file and directory permission to a user.

```console
[root@ansible ~]# dnf install acl
[root@ansible ~]# setfacl -R -m g:ansible:rwx /etc/ansible/
```

We can confirm with `ls -l` if the group permissions are assigned correctly.

```console

[root@ansible]# ls -l
total 48
-rw-rwxr--+ 1 root g-ansible  614 Feb 10 00:00 ansible.cfg
-rw-rwxr--+ 1 root g-ansible 1175 Feb 10 00:00 hosts
drwxrwsr-x+ 2 root g-ansible 4096 Jun  2 18:28 playbooks
drwxrwsr-x+ 2 root g-ansible 4096 Jun  2 17:46 prod
-rw-rwxr--+ 1 root g-ansible  151 Jun  7 08:37 prod.ini
drwxrwsr-x+ 2 root g-ansible 4096 Jun  2 17:46 roles

```

The final step is setting up the SSH key the ansible user will use to connect safely to the other systems. To do that, use the `su` command to log into the ansible user out of the root user session. Use the default values and a passphrase if needed.



```console
[root@ansible ~]# su ansible
[ansible@ansible ~] ssh-keygen
```

Once the key is installed you will need to create an ansible user on the relevant target systems and deploy the public key to its authorized keys for SSH authentication. Once done, verify the connection by connection to the target systems using SSH from the Ansible host. 

!!! note
  Please make sure the Ansible user on the target systems has the required sudo privileges **AND** that the user does not need a password to escalate its privileges. For the beginning you can give the Ansible user root access, but it is safer to reduce the granted permissions only to the necessary once.


### Inventory Setup




