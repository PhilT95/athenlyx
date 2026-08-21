# Semaphore Setup Guide - AlmaLinux 10

Even though [Ansible](index.md) is a very good automation tool it certainly lacks the modern approach of managing it. This is where [Semaphore](https://semaphoreui.com/) comes into play. It builds upon the Ansible toolset and extends it with

- A web-based GUI to interact with Ansible
- Easy Inventory, User and Playbook Management
- Key Management including a database where SSH Keys & passwords can be stored securely
- Scheduling and logging of Task Executions with various integration to always be notified about problems with ansible

It even comes with Repository Management and Git Integrations which makes versioning tasks and inventories trivial.

This guide will therefore show the installation and setup of Semaphore. It is recommended by Semaphore itself to use the docker installation since its simplicity makes it an easy way to get Semaphore started. But this guide will focus on the local installation using the AlmaLinux package manager since this is less well documented by Semaphore. If you still want to install it using docker you can follow the [official Semaphore Guide](https://semaphoreui.com/docs/admin-guide/installation/docker).

## Requirements

Before we can start with the installation of Semaphore please make sure the following requirements are fulfilled:

- [x] An AlmaLinux 10 system with
    - [X] Ansible installed and running
    - [X] SSH and root access
    - [X] Internet access
- [X] Able to access the system using https via port 3309 (Default Semaphore Port)
- [X] An functioning Ansible setup including
    - [X] Playbooks
    - [X] Inventories
    - [X] Access to machines listed in inventories (optional) 


!!! tip "Installing Ansible"
    If you haven't installed and configured Ansible itself yet you can follow this [Ansible Setup Guide](ansible_setup.md) to get a basic setup.


## Installation

### Getting the system up-to-date

At first we have to install all updates and make sure the newest updates are installed. Connect to the target system and execute the command below.

```bash
sudo dnf update -y
```

### Installing & setting up MariaDB

Once the system has all updates installed we need to setup a database instance which Semaphore can connect to and use it to store login details for example. We will use MariaDB since its setup is easy and sufficient for this setup.

!!! note
    Semaphore can also connect to a remote database. In this case please make sure to setup the required database and permissions on the remote database instead.

```bash
# Installing the MariaDB server package
sudo dnf install mariadb-server -y

# Setting up the MariaDB server as a system service
sudo systemctl enable mariadb
sudo systemctl start mariadb
```

Now that the MariaDB server is running we need to setup the database and user which Semaphore will be using. We need to get into the MariaDB CLI and from there we can continue.

```bash
sudo mariadb
```

Now we will create a user `semaphore` which needs a password you need to provide yourself. Then we create the database and grant the necessary privileges for it to the user.

```mysql
CREATE USER 'semaphore'@'localhost' IDENTIFIED BY 'password';
CREATE DATABASE semaphore;
GRANT ALL PRIVILEGES ON semaphore.* TO 'semaphore'@'localhost';
FLUSH PRIVILEGES;
```

Exit the MariaDB CLI with `exit`.

### Installing Semaphore

With the database set up we can start installing Semaphore itself. Since there is now prepared package provided by the package manager we have to download the package ourselves. Navigate to the [Semaphore Relase page](https://github.com/semaphoreui/semaphore/releases) and copy the link of the most recent `rpm` file.

??? example "Download Link Version 2.19.8"
    Here is the download link for the [Version 2.19.8](https://github.com/semaphoreui/semaphore/releases/download/v2.19.8/semaphore_2.19.8_linux_amd64.rpm)

Now we can download the package and install it using the package manager.

```bash
# Downloading the package
wget https://github.com/semaphoreui/semaphore/releases/download/v2.19.8/semaphore_2.19.8_linux_amd64.rpm

# Installing the package
sudo dnf install semaphore_2.19.8_linux_amd64.rpm -y
```

### Setting up Semaphore







