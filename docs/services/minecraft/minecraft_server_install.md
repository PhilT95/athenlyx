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

Now there should be a JAR-file within the "server" directory. To install it, we will switch into the minecraft user since we won't need sudo permissions for the installation and go by the Least Privilege principle.

```console
[root@minecraftserver server]# su minecraft
[minecraft@minecraftserver server]$ java -jar forge-26.1.2-64.0.8-installer.jar --installServer
```

Now the installer will setup the `server` directory with all configuration and the server file itself. The directory now should look mostly like this.

```console
[minecraft@minecraftserver server]$ tree -L 1
.
├── backups
├── banned-ips.json
├── banned-players.json
├── config
├── defaultconfigs
├── eula.txt
├── forge-26.1.2-64.0.8-installer.jar.log
├── forge-26.1.2-64.0.8-shim.jar
├── libraries
├── logs
├── mods
├── ops.json
├── README.txt
├── run.bat
├── run.sh
├── server-icon.png
├── server.properties
├── usercache.json
├── user_jvm_args.txt
├── usernamecache.json
├── whitelist.json
└── world
```

Now we are ready to configure the server for its first run.

### Preparing the server start

To start the server successfully, we need 

1. To accept the EULA by editing the `eula.txt` file
2. Prepare the server start script
3. Configure a few JVM settings

Accepting the EULA is a simple task. We just need to open the file and change `eula=false` to `eula=true`.

```console
[minecraft@minecraftserver server]$ nano eula.txt
```

Now we start preparing the file that will be used to start the server. It is a simple shell script. If it not already exists, create a `run.sh` file.

```console
[minecraft@minecraftserver server]$ nano run.sh
```

The file should look like this.

```shell
#!/usr/bin/env sh
# Add custom JVM arguments (such as RAM allocation) to the user_jvm_args.txt

java -jar forge-26.1.2-64.0.8-shim.jar --onlyCheckJava || exit 1

# Add custom program arguments (such as nogui) to the next line before the "$@" or pass them to this script directly
java @user_jvm_args.txt @libraries/net/minecraftforge/forge/26.1.2-64.0.8/unix_args.txt --nogui "$@"
```

Save the file and open `user_jvm_args.txt` and if it doesn't exist, create it.

```console
[minecraft@minecraftserver server]$ nano user_jvm_args.txt
```

Within this file we set the minimum and maximum amount of RAM the Minecraft server should use. In this example we will set the lower limit to 4 GB and the upper limit to 6750 MB. You can also leave this empty and let the server decide itself how much RAM it should take.

!!! note
    The upper limit has been set up like this to keep enough RAM for the OS itself on a system with a total of 8 GB of RAM.

```txt
# Note: Not all server panels support this file. You may need to set these options in the panel itself.

# Xmx and Xms set the maximum and minimum RAM usage, respectively.
# They can take any number, followed by an M (for megabyte) or a G (for gigabyte).
# For example, to set the maximum to 3GB: -Xmx3G
# To set the minimum to 2.5GB: -Xms2500M

# A good default for a modded server is 4GB. Do not allocate excessive amounts of RAM as too much may cause lag or crashes.
# Uncomment the next line to set it. To uncomment, remove the # at the beginning of the line.
# -Xmx4G

-Xms4G
-Xmx6750M
```

Now everything is set up to start the server for the first time. Just execute the following command and the server will boot.

```console
[minecraft@minecraftserver server]$ ./run.sh
```

### Setup the server as a service

Now that the server is running we can see that it is running directly from the minecraft user session. If something happens to the user session (logoff, shutdown etc.) the Minecraft server will stop and has to be restarted manually. To simplify this we will implement the application as a system service running in the background in the context of the minecraft user without a need to be logged in.

For this step we will need to go back into the root session that we used to get into the minecraft user session. Then we need to register the Minecraft server service and enable it.

```
[minecraft@minecraftserver server]$ exit
exit
[root@minecraftserver server]$ nano /etc/systemd/system/minecraft.service
```

In the file that we are creating now, copy the following

```systemd
[Unit]
Description=Minecraft 26.1.2 Server
After=network.target

[Service]
User=minecraft
WorkingDirectory=/home/minecraft/server
ExecStart=/home/minecraft/server/run.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

This tells the system that it the process starter here will be accessible through the network, where the files are located, how to start the system and how to behave in case of a restart. It also states that the process will be started using the minecraft user.

Once this file is created we need to tell `systemd` to enable and start it.


```console
[root@minecraftserver server]$ systemctl enable minecraft
[root@minecraftserver server]$ systemctl start minecraft
```

Now your server should run without any problems and you can start or stop the server in the background by using `systemctl start minecraft` or `systemctl stop minecraft`.

### Configuring the local firewall

Since we are exposing a network service from our system it is best practice to lock down the network interface by only allowing connection to relevant ports.
