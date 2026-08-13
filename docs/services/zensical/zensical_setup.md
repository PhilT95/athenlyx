# Zensical Setup on AlmaLinux 10

This guide will help you setup Zensical on a system running AlmaLinux 10 and how publish them using nginx.


## Requirements

The Zensical setup is a very straight-forward process and does not differ a lot from other Linux distributions but there are a few things that you should have ready.

- [x] A system running AlmaLinux 10 with
    - [X] SSH access
    - [X] Root permissions
    - [X] Internet access
- [X] A basic understanding how to interact with a shell

## Setup

### Login & Update

To begin with the Zensical setup, connect to your system using SSH. Once logged in we will make the system is up-to-date. Since we need root permissions to update the system and will be needing these permissions to install all required components as well we switch into the root session using the ``su`` command.

```console
[user@zensical ~]$ sudo su
[root@zensical user]# dnf update -y
```

### Installation Dependency & Zensical

Once the updates are installed we can continue with the installation of all Zensical dependencies and Zensical itself.