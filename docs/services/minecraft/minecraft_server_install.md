# Minecraft Java Server Installation Guide for AlmaLinux 10 - with Mods

In this guide we will setup a Minecraft Java server with mod support on an AlmaLinux 10 system and add basic configuration to let the server run automatically as a service on the server.

## Requirements

Before we need the following requirements before continuing with the setup

- An AlmaLinux 10 system
    * [x] with at least 2 cores
    * [x] with at least 30 GB of storage space
    * [x] with at least 4 GB of RAM
    * [x] that has access to the internet
- [x] Root access to the system
- [x] SSH access to the system

!!! tip "AlmaLinux 10 Setup"
    If you don't know how to setup an AlmaLinux 10 system you can refer to [this](../../linux-admin/rhel-alma/almalinux_setup.md) guide which will help you set up a new user with root access.


## Setup

### Preparing the system

Before we can start installing and configuring the server we need to install the dependencies to run Minecraft. That includes updating the server and installing the required Java version. Since we need root access, we first ensure that we have the permission. Keep the root / sudo password ready.

```console
[user@minecraftserver ~]$ sudo su
[sudo] password for user:
[root@minecraftserver user]# 
```

Now that we elevated the session into a sudo session we can begin updating and installing all required components.

```console
[root@minecraftserver user]# dnf update -y
[root@minecraftserver user]# dnf install java-21-openjdk-headless wget -y
```

### Setting up a system user

To separate and isolate the Minecraft server process we will let it run using a different user which will not have root access. 

```console
[root@minecraftserver user]# useradd -r -s /bin/bash minecraft
```

This command will create the user `minecraft`. The `-r` option sets the flag that this will be a system account and the `-s /bin/bash` flag tells it to use `bash` as its login shell.

!!! note
    You can give the account you create any name you want by changing `minecraft` to the name you want to use.


### Downloading and preparing the Minecraft server application

First we will navigate to the home directory of the user we just created to prepare the place where we will keep and run all files related to minecraft.

```console
[root@minecraftserver user]# mkdir /home/minecraft/server
[root@minecraftserver user]# cd /home/minecraft/server
```

Now we have to download the server application. Since we want to enable mods, we can't download the installer directly from Microsoft since *Vanilla* Minecraft does not support mods. We can get it for example from **Minecraft Forge**. Follow [this](https://files.minecraftforge.net/net/minecraftforge/forge/) link to all available Minecraft server versions and pick the one you want to install, then download the installer from the website. 

??? tip "Download the installer directly to your server"
    You can download the installer directly to your server using the `wget` command.

    ```console
    [root@minecraftserver server]# wget https://maven.minecraftforge.net/net/minecraftforge/forge/26.2-65.0.1/forge-26.2-65.0.1-installer.jar
    --2026-06-29 17:16:30--  https://maven.minecraftforge.net/net/minecraftforge/forge/26.2-65.0.1/forge-26.2-65.0.1-installer.jar
    Resolving maven.minecraftforge.net (maven.minecraftforge.net)... 172.67.161.211, 104.21.58.163, 2606:4700:3032::6815:3aa3, ...
    Connecting to maven.minecraftforge.net (maven.minecraftforge.net)|172.67.161.211|:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 7853602 (7.5M) [application/java-archive]
    Saving to: ‘forge-26.2-65.0.1-installer.jar’

    forge-26.2-65.0.1-installer.jar                                         100%[=============================================================================================================================================================================>]   7.49M  --.-KB/s    in 0.06s

    2026-06-29 17:16:30 (117 MB/s) - ‘forge-26.2-65.0.1-installer.jar’ saved [7853602/7853602]

    ```

    Make sure to look at the link if when copying from the website since minecraftforge.net adds an ad redirect to it that needs to be removed before.

