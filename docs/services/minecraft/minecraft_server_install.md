# Minecraft Java server installation guide for AlmaLinux 10 - with mod support

With this guide you are going to setup a Minecraft Java server with mod support on an AlmaLinux 10 system and add basic configuration to let the server run automatically as a service on the server.

## Requirements

Before you can start with the setup guide please ensure that you fulfill the following requirements:

- [x] An AlmaLinux 10 system
    * [x] with at least 2 cores
    * [x] with at least 30 GB of storage space
    * [x] with at least 4 GB of RAM
    * [x] that has access to the internet
- [x] Root access to the system
- [x] SSH access to the system

!!! tip "AlmaLinux 10 Setup"
    If you don't know how to setup an AlmaLinux 10 system you can refer to [this](../../linux-admin/rhel-alma/almalinux_setup.md) guide which provides more information on how to set up a new user with root access.


## Setup

### Preparing the system

Before you can start installing and configuring the server you need to install the dependencies to run Minecraft. That includes updating the server and installing the required Java version. Since need root access is required, first ensure that you have the permission. Keep the root / sudo password ready.

```bash
sudo su
```

Now that you elevated the session into a sudo session begin updating and installing all required components.

```bash
dnf update -y
dnf install java-21-openjdk-headless wget -y
```

### Setting up a system user

To separate and isolate the Minecraft server process you should let it run using a different user which is not going to have root access. 

```bash
useradd -r -s /bin/bash minecraft
```

This command creates the user `minecraft`. The `-r` option sets the flag that this is a system account and the `-s /bin/bash` flag tells it to use `bash` as its login shell.

!!! note
    You can give the account you create any name you want by changing `minecraft` to the name you want to use.


---

### Downloading and preparing the Minecraft server application

First you need to navigate to the home directory of the user that was just created to prepare the location where all files related to minecraft are kept.

```bash
mkdir /home/minecraft/server
cd /home/minecraft/server
```

Now you have to download the server application. Since you want to enable mods, you can't download the installer directly from Microsoft because *Vanilla* Minecraft does not support mods. You can get it for example from **Minecraft Forge**. Follow [this](https://files.minecraftforge.net/net/minecraftforge/forge/) link to all available Minecraft server versions and pick the one you want to install, then download the installer from the website. 

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

Now there should be a JAR-file within the "server" directory. To install it, you need to switch into a minecraft user session. This works since the installation doesn't require sudo permissions.

```bash
su minecraft
java -jar forge-26.1.2-64.0.8-installer.jar --installServer
```

Now the installer is preparing the `server` directory with all configuration and the server file itself. The directory now should look similar to the following one:

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

Now you are ready to configure the server for its first run.

---

### Preparing the server start

To start the server successfully, you need 

1. To accept the EULA by editing the `eula.txt` file
2. Prepare the server start script
3. Configure a few JVM settings

Accepting the EULA is a simple task. You just need to open the text file and change `eula=false` to `eula=true`.

```bash
nano eula.txt
```

Now you need to prepare the shell script file that is going to start the server. If it not already exists, create a `run.sh` file.

```bash
nano run.sh
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

```bash
nano user_jvm_args.txt
```

Within this file you can set the minimum and maximum amount of RAM the Minecraft server should use. In this example the lower limit is set to 4 GB and the upper limit to 6750 MB. You can also leave this empty and let the server decide itself how much RAM it should take.

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

Now everything is set up to start the server for the first time. Just execute the following command and the server is going to boot.

```bash
./run.sh
```

---

### Setup the server as a service

Now that the server is running you can observe that it is running directly from the minecraft user session. If something happens to the user session (logoff, shutdown etc.) the Minecraft server stops and has to be restarted manually. To simplify this you can implement the application as a system service running in the background in the context of the minecraft user without a need to be logged in.

For this step you need to go back into the root session that you used to get into the minecraft user session. Then register the Minecraft server service and enable it.

```bash
exit
nano /etc/systemd/system/minecraft.service
```

In the file that you are creating now, copy the following content:

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

This tells the system that the process should be accessible through the network, where the files are located, how to start the system and how to behave in case of a restart. It also states that the process is run by the minecraft user.

Once this file is created you need to tell `systemd` to enable and start it.


```bash
systemctl enable minecraft
systemctl start minecraft
```

Now your server should run without any problems and you can start or stop the server in the background by using `systemctl start minecraft` or `systemctl stop minecraft`. 

---

### Configuring the local firewall

Since you are exposing a network service from your system it is best practice to lock down the network interface by only allowing connection to relevant ports. Since the Minecraft server application uses the port 25565 as a standard, you need to keep this port and SSH for management open to the system. AlmaLinux comes with a pre-installed but not enabled local firewall called [firewalld](../../linux-admin/rhel-alma/firewalld.md), which you can use. With AlmaLinux 10, firewalld is already bundled with a Minecraft service template which you can verify by accessing its configuration file at `/usr/lib/firewalld/services/minecraft.xml`. The file should look like this:

```xml
<service>
  <short>Minecraft</short>
  <description>
    Minecraft is a sandbox game developed by Mojang Studios.
  </description>
  <port protocol="tcp" port="25565"/>
  <port protocol="udp" port="25565"/>
</service>
```

If the file does not exist, create it and add the information from XML snippet, then safe the file. Once that is done you have to create a firewall rule that allows incoming traffic using the required ports.

Before you can setup `firewalld` you need to enable and start the service so it can permanently run within the system context.

```bash
systemctl enable firewalld
systemctl start firewalld
```

Once the `firewalld` service is running you can add the minecraft service, reload the ruleset and verify the configuration.


```console
[root@minecraftserver server]$ firewall-cmd --add-service minecraft --zone=public --permanent
success
[root@minecraftserver server]$ firewall-cmd --reload
success
[root@minecraftserver server]$ firewall-cmd --list-all
public (default, active)
  target: default
  ingress-priority: 0
  egress-priority: 0
  icmp-block-inversion: no
  interfaces: eth0
  sources:
  services: cockpit dhcpv6-client minecraft ssh
  ports:
  protocols:
  forward: yes
  masquerade: no
  forward-ports:
  source-ports:
  icmp-blocks:
  rich rules:
```

The configuration should now look similar to the preceding output. It is important that `minecraft` is listed here. At this point your minecraft server should be able to be accessed through the Minecraft client.

!!! note "Accessing the server through the internet"
    Please make sure that the server is actually reachable through the internet, especially that the ports are not blocked by any other network device like routers or firewalls. Port-Forwarding may need to be enabled depending on your setup.

    Also note that the server might be reachable, but to login, please continue following the guide.

---

### Setting up users

Minecraft servers use the authentication via Minecraft (now Microsoft) Accounts. Using this method, to add allow a player to connect to the server you need to add him to the list of allowed players. While doing that, you can also give the player you whitelist the *Operator* status, granting him administrator commands. 

For this step you need to enter the server command line. First you have to stop the minecraft service that you setup earlier before you can continue setting up the Operator account for the server.


```console
[root@minecraftserver server]# systemctl stop minecraft
[root@minecraftserver server]# su minecraft
[minecraft@minecraft01 server]$ ./run.sh
[13:53:08] [main/INFO] [cp.mo.mo.Launcher/MODLAUNCHER]: ModLauncher running: args [--launchTarget, forge_server, --nogui]
[13:53:08] [main/INFO] [cp.mo.mo.Launcher/MODLAUNCHER]: JVM identified as Red Hat, Inc. OpenJDK 64-Bit Server VM 25.0.3+9-LTS
[13:53:08] [main/INFO] [cp.mo.mo.Launcher/MODLAUNCHER]: ModLauncher 10.2.4 starting: java version 25.0.3 by Red Hat, Inc.; OS Linux arch amd64 version 6.12.0-211.7.4.el10_2.x86_64
[13:53:08] [main/INFO] [ne.mi.fm.lo.ImmediateWindowHandler/]: ImmediateWindowProvider not loading because launch target is forge_server
[13:53:08] [main/INFO] [mixin/]: SpongePowered MIXIN Subsystem Version=0.8.7 Source=jar:file:///home/minecraft/server/libraries/org/spongepowered/mixin/0.8.7/mixin-0.8.7.jar!/ Service=ModLauncher Env=SERVER
[13:53:09] [main/INFO] [ne.mi.fm.lo.mo.JarInJarDependencyLocator/]: No dependencies to load found. Skipping!
[13:53:09] [main/INFO] [cp.mo.mo.LaunchServiceHandler/MODLAUNCHER]: Launching target 'forge_server' with arguments [--nogui]
Jul 13, 2026 1:53:15 PM de.gnm.voxeldash.VoxelDashMod <init>
INFO: Starting VoxelDash Forge...
[13:53:15] [modloading-worker-0/INFO] [ne.mi.co.ForgeMod/FORGEMOD]: Forge mod loading, version 64.0.8, for MC 26.1.2 with MCP 20260409.101008
[13:53:15] [modloading-worker-0/INFO] [ne.mi.co.MinecraftForge/FORGE]: MinecraftForge v64.0.8 Initialized
[13:53:15] [modloading-worker-0/INFO] [ne.mi.co.ForgeMod/FORGEMOD]: Opening jdk.naming.dns/com.sun.jndi.dns to java.naming
[13:53:15] [Forge Version Check/INFO] [ne.mi.fm.VersionChecker/]: [forge] Starting version check at https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json
[13:53:16] [Forge Version Check/INFO] [ne.mi.fm.VersionChecker/]: [forge] Found status: BETA_OUTDATED Current: 64.0.8 Target: 64.0.11
[13:53:16] [main/INFO] [mojang/YggdrasilAuthenticationService]: Environment: Environment[sessionHost=https://sessionserver.mojang.com, servicesHost=https://api.minecraftservices.com, profilesHost=https://api.mojang.com, name=PROD]
[13:53:18] [main/INFO] [minecraft/RecipeManager]: Loaded 1515 recipes
[13:53:18] [main/INFO] [minecraft/AdvancementTree]: Loaded 1617 advancements
[13:53:18] [Server thread/INFO] [minecraft/DedicatedServer]: Starting minecraft server version 26.1.2
[13:53:18] [Server thread/INFO] [minecraft/DedicatedServer]: Loading properties
[13:53:18] [Server thread/INFO] [minecraft/DedicatedServer]: Default game type: SURVIVAL
[13:53:18] [Server thread/INFO] [minecraft/MinecraftServer]: Generating keypair
[13:53:18] [Server thread/INFO] [minecraft/DedicatedServer]: Starting Minecraft server on *:25565
[13:53:19] [Server thread/INFO] [minecraft/DedicatedServer]: Preparing level "grafenberg"
[13:53:19] [Server thread/INFO] [minecraft/LoggingLevelLoadListener]: Loading 0 persistent chunks...
[13:53:19] [Server thread/INFO] [minecraft/LoggingLevelLoadListener]: Preparing spawn area: 100%
[13:53:19] [Server thread/INFO] [minecraft/LoggingLevelLoadListener]: Time elapsed: 15 ms
[13:53:19] [Server thread/INFO] [minecraft/DedicatedServer]: Done (0.335s)! For help, type "help"
....
```

After starting this server you should see a similar output. Once the server start sequence is done your console should look like this:

```console
[13:54:20] [Server thread/INFO] [minecraft/MinecraftServer]: Server empty for 60 seconds, pausing
>
```

The **>** sign indicated that the minecraft server console is now available. Here you can now add user accounts and promote them to Operators.

```console
> whitelist add PlayerName
[13:59:18] [Server thread/INFO] [minecraft/MinecraftServer]: Player is whitelisted
> op ScarBytes
[13:59:58] [Server thread/INFO] [minecraft/MinecraftServer]: Player promoted to operator
```

Once this is done you can safely shutdown the server by pressing ++crtl+c++ together. Now start the server again using `systemctl`.

!!! warning
    Before you start the service, make sure you are back into the root shell.

    ```console
    [minecraft@minecraft01 server]$ exit
    [root@minecraft01 server]#
    ```

```bash
systemctl start minecraft
```

Now the server should be up and running and the user you added can log into the server using your minecraft client.

!!! tip
    Once you're logged into your server you can use the console inside the game to add users and promote them to Operators without needing to restart the server or reloading the setting from the shell.

