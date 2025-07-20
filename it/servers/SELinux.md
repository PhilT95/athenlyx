# SELinux 

The SELinux config file is located under /etc/selinux/config

## General setup

### Set SELinux to Enforcing

1. `nano /etc/selinux/config`
2. Set the parameter `SELINUX` from `Permissive` to `Enforcing`. The line should read `SELINUX=ENFORCING`