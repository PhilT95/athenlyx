# AlmaLinux Setup Guide
This guide provided a few easy steps get a rather secure baseline AlmaLinux installation. The installation of AlmaLinux itself can be found at the [AlmaLinux Wiki](https://wiki.almalinux.org/documentation/installation-guide.html).

## The Basics 
Before you start installing applications or anything else, make sure you do the following few tasks:

1. Create a separate user with sudo permissions
2. Enable login via SSH using a private key for this user
3. Disable direct root login via ssh

### Create a new user with sudo permissions
Follow these steps to create a new user with sudo permissions. You need root permissions to fulfill these steps

1. `useradd username` -> Creates the user with the given name
2. `passwd username` -> Lets you create a password for the user
3. `usermod -aG wheel username` -> Assigns the user to the group wheel. This is the sudoer-group within AlmaLinux
4. Create a file called within the newly created users home directory called **authorized_keys** under `~/.ssh/`. You might need to create the directory first. Copy your public key into this file and save it.
5. Make sure the Setting **PermitRootLogin** within the ssh config files in the directory `/etc/ssh/` is set to **No**
