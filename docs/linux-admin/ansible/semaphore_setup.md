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


## Installation

### Getting the system up-to-date

At first we have to install all updates and make sure the newest updates are installed.

```console

```

### Installing the dependencies

