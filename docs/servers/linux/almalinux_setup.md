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
5. Make sure the Setting **PermitRootLogin** within the ssh config files in the directory `/etc/ssh/` is set to **No**. The file usually is called `sshd_config`

## Installing Tools and Applications

### Installing Docker

AlmaLinux comes with podman instead of Docker. If the usage of your server requires Docker instead, you can follow these steps.

#### Update your system

Always update your system's package repositories to ensure you getting the latest versions.

```console
sudo dnf --refresh update
sudo dnf upgrade
```

#### Enable Docker Repository

To install docker, you need to add the official docker repository to your package manager. You need the `yum-utils` package to configure the package manager.

```console
sudo dnf install yum-utils
```

After installing this package you can add the repository.

```console
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
```

#### Installing Docker

Now you can install the docker packages using the default package manger from the official Docker repository itself.

```
sudo dnf install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

!!! info
    This command also installs a few additional tools. Especially the docker-compose-plugin is often a necessity.

#### Enabling Docker

To let docker run as a service on your system, you need to start and enable it within **systemd**.

```console
sudo systemctl start docker
sudo systemctl enable docker
```


