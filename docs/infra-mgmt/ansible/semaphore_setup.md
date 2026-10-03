# Semaphore setup guide - AlmaLinux 10

Even though [Ansible](index.md) is a useful automation tool it certainly lacks the modern approach of managing it. This is where [Semaphore](https://semaphoreui.com/) comes into play. It builds upon the Ansible toolset and extends it with

- A web-based GUI to interact with Ansible
- Easy Inventory, User, and Playbook Management
- Key Management including a database where SSH Keys & passwords can be stored securely
- Scheduling and logging of Task Executions with many integrations to always be notified about problems with ansible

It even comes with Repository Management and Git Integrations which makes versioning tasks and inventories trivial.

This guide therefore provides the steps for the installation and setup of Semaphore. Semaphore recommends using the docker installation for its simplicity, But this guide is focusing on the local installation using the AlmaLinux package manager since this is less documented. If rather want to install Semaphore using docker you can follow the [official Semaphore Guide](https://semaphoreui.com/docs/admin-guide/installation/docker).

## Requirements

Before you can start with the installation of Semaphore please make sure the following requirements are met:

- [x] An AlmaLinux 10 system with
    - [X] Ansible installed and running
    - [X] SSH and root access
    - [X] Internet access
- [X] Able to access the system using HTTP via port 3309 (Default Semaphore Port)
- [X] An functioning Ansible setup including
    - [X] Playbooks
    - [X] Inventories
    - [X] Access to machines listed in inventories (optional) 


!!! tip "Installing Ansible"
    If you haven't installed and configured Ansible itself yet you can follow this [Ansible Setup Guide](ansible_setup.md) to get a basic setup.


## Installation

### Getting the system up-to-date

At first you have to install all updates and make sure the newest updates are installed. Connect to the target system and execute the command below.

```bash
sudo dnf update -y
```

### Installing & setting up MariaDB

Once the system has all updates installed you need to setup a database instance which Semaphore can connect to and use it to store login details for example. You can use MariaDB since its setup is easy and sufficient for this setup.

!!! note
    Semaphore can also connect to a remote database. In this case please make sure to setup the required database and permissions on the remote database instead.

```bash
# Installing the MariaDB server package
sudo dnf install mariadb-server -y

# Setting up the MariaDB server as a system service
sudo systemctl enable mariadb
sudo systemctl start mariadb
```

Now that the MariaDB server is running you need to setup the database and user which Semaphore is going to use. You need to get into the MariaDB CLI to continue.

```bash
sudo mariadb
```

Now you need to create a `semaphore` user with a password that you need to set. Then create the database and grant the necessary privileges to the user.

```mysql
CREATE USER 'semaphore'@'localhost' IDENTIFIED BY 'password';
CREATE DATABASE semaphore;
GRANT ALL PRIVILEGES ON semaphore.* TO 'semaphore'@'localhost';
FLUSH PRIVILEGES;
```

Exit the MariaDB CLI with `exit`.

### Installing Semaphore

With the database ready you can start installing Semaphore. Since no prepared package provided by the package manager exists you need to download the package manually. Navigate to the [Semaphore Release page](https://github.com/semaphoreui/semaphore/releases) and copy the link of the most recent `rpm` file.

??? example "Download Link Version 2.19.8"
    Here is the download link for the [Version 2.19.8](https://github.com/semaphoreui/semaphore/releases/download/v2.19.8/semaphore_2.19.8_linux_amd64.rpm)

Now you can download the package and install it using the package manager.

```bash
# Downloading the package
wget https://github.com/semaphoreui/semaphore/releases/download/v2.19.8/semaphore_2.19.8_linux_amd64.rpm

# Installing the package
sudo dnf install semaphore_2.19.8_linux_amd64.rpm -y
```

### Setting up Semaphore

Semaphore provides its own setup creation process which is gathering all required information and creates a configuration file for running the application. For this purpose create a new configuration directory for Semaphore where the configuration file is saved to.

```bash
mkdir /etc/semaphore && cd /etc/semaphore
semaphore setup
```

Once you start the setup configuration provide the details for the setup. Your answers should look similar to the ones below:

```console title="Semaphore setup"
Hello! You will now be guided through a setup to:

1. Set up configuration for a MySQL/MariaDB database
2. Set up a path for your playbooks (auto-created)
3. Run database Migrations
4. Set up initial semaphore user & password

What database to use:
   1 - MySQL
   2 - BoltDB (DEPRECATED!!!)
   3 - PostgreSQL
   4 - SQLite
 (default 1): 1

db Hostname (default 127.0.0.1:3306):

db User (default root): semaphore

db Password:

db Name (default semaphore): ^C
[root@command tmp]# semaphore setup

Hello! You will now be guided through a setup to:

1. Set up configuration for a MySQL/MariaDB database
2. Set up a path for your playbooks (auto-created)
3. Run database Migrations
4. Set up initial semaphore user & password

What database to use:
   1 - MySQL
   2 - BoltDB (DEPRECATED!!!)
   3 - PostgreSQL
   4 - SQLite
 (default 1): 1

db Hostname (default 127.0.0.1:3306):

db User (default root): semaphore

db Password: <your-password>

db Name (default semaphore):

Playbook path (default /tmp/semaphore): /etc/semaphore/playbooks

Public URL (optional, example: https://example.com/semaphore):

Enable email alerts? (yes/no) (default no):

Enable telegram alerts? (yes/no) (default no):

Enable slack alerts? (yes/no) (default no):

Enable Rocket.Chat alerts? (yes/no) (default no):

Enable Microsoft Team Channel alerts? (yes/no) (default no):

Enable LDAP authentication? (yes/no) (default no):

Config output directory (default /tmp): /etc/semaphore

```

Once you finish the last step the tool verifies database access and creates a configuration file with the details. 

```json title="Example Configuration file"
{
        "mysql": {
                "host": "127.0.0.1:3306",
                "user": "semaphore",
                "pass": "your-password",
                "name": "semaphore"
        },
        "dialect": "mysql",
        "tmp_path": "/etc/semaphore/playbooks",
        "cookie_hash": "some_hash",
        "cookie_encryption": "some_hash",
        "access_key_encryption": "some_hash"
 }

```

Using this configuration file you can start the Semaphore UI application.

```bash
sudo semaphore server --config /etc/semaphore/config.json
```

If everything is setup correctly you can now access the web application through **http://localhost:3000/**. You can login using the username and credentials you created and used during the Semaphore setup.

## Semaphore configuration

Now that you can access Semaphore through its WebUI continue setting up the rest using the web frontend. Once you're logged in you're greeted with a prompt to create a *Project*. A project contains the repositories, task templates, credentials and more that should to be used within the same context. Provide a name for the project and click **Create**. Once this is done you should see the dashboard of this project.

![Semaphore Dashboard](images/sempahore_dashboard.png)

### Key store

The first step is adding the credentials used/required by Ansible to the key store. Navigate to the **Key Store** menu on the left. There click **New Key** on the top left. Set the **type** to **SSH Key** and provide the username, private key and optionally the passphrase that goes with it.

![Semaphore Create Credentials](images/sempahore_new-credential.png)

!!! note
    You can also create users with or without any password at all by switching the type while creating the credentials.

### Repository 

For the next step create a repository referencing the local path to the directory where your playbooks and inventories are stored. On the menu list to the left navigate to **Repositories**. There, again in the upper right corner, click **New repository**.

!!! note
    If you are already using git for your repository you can also connect to your local or remote git. Please be aware that you need to provide the correct credentials if the connection to a remote git is required.

Give the repository a new, provide the path (or URL) to it as well as credentials if required. If there are no credentials needed, set the Access Key to **None**, then click **Create**.

![Semaphore Create Repository](images/sempahore_new-repository.png)


### Inventory

Before you can integrate the playbooks you need to setup the inventory inside Semaphore. Click the **Inventory** menu through the lift on the list and use the **New Inventory** menu on the top right corner. Make sure you select **Ansible Inventory**.

This *Creation Menu* offers 3 different ways to create inventories:

- **Static**: creates a inventory file with the content provided in the menu itself.
- **Static YAML**: same at the static option, except that Semaphore now expects a YAML structure.
- **File**: provide the path to an inventory file on the system. You can optionally provide the related repository.

In this case you have to link it to an existing inventory. Give the inventory a name, provide credentials if needed and the path to the Ansible inventory file. Once everything is filled out click **Create**.

![Semaphore Create Inventory](images/sempahore_new-inventory.png)

### Task template

With everything else set up you can finally create a **Task Template** which links and uses an Ansible playbook. Navigate to **Task Templates**, click **New Template**, and then select **Ansible Playbook**. 

![Semaphore Create Task Template](images/sempahore_new-playbook.png)

You can see a lot of different fields, but for now focus on the basic ones to get the playbook running. Give the Task Template a name, provide the path to the playbook on the system, and select the inventory as well as the repository created earlier. Click **Create** to create the template.

## Run and schedule a Task

Now that you created everything that's needed for a Task to run, navigate to the **Task Templates** menu again. Click the **Play** Button which starts the Ansible Task. A new window appears showing you the log for this task.

Once your task runs without issues go into the **Schedule** menu, click **New Schedule** and use the **cron** option. Now you can select a Task Template and configure the time and day at which the task should be running automatically.

![Semaphore Create Task Schedule](images/sempahore_new-schedule.png)

