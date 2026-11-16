# Plausible analytics setup guide for AlmaLinux 10

This guide provides the steps to install and setup **Plausible analytics - CE** on an AlmaLinux 10 system using Docker. The targeted version for this setup is ``v3.2.1``. If you want to install any other version you should just be able to change the version number in the installation step.

!!! note
    Please be aware that there is no official non-Docker setup. For more information refer to the [official Plausible GitHub page](https://github.com/plausible/community-edition).

## Requirements

The Plausible setup is Docker-based and therefore simple but there are still a few things required for a smooth installation.

- [x] A system running AlmaLinux 10 with
    - [x] SSH access
    - [x] Root permissions
    - [x] Internet access
- [x] A basic understanding of docker and the Linux shell
- [x] A domain which can be used to host Plausible 

## Setup

### System update

Before you can start with the actual installation, setup, and integration of Plausible you need to ensure that you are logged into the system and it is up to date. Once you are logged into the system using SSH update the system.

```bash
sudo dnf update -y
```

This ensures that the system is fully up to date. If required reboot the system and log in again once it is up.

### Installing prerequisites

Since the installation requires Docker, please refer to the [AlmaLinux 10 Setup Guide](../../infra-mgmt/linux-admin/rhel-alma/almalinux_setup.md#installing-docker) for these steps. Once you are done with the docker installation the only needed prerequisite left is git.

```bash
sudo dnf install git -y
```

### Installing Plausible

To install the most recent version of Plausible, please visit the [Plausible CE GitHub Page](https://github.com/plausible/community-edition/) and search for the last published version. Once you have the version you can download the repository using the version tag.

```bash
git clone -b v3.2.1 --single-branch https://github.com/plausible/community-edition plausible-ce
```

Once you downloaded the repository, navigate into the newly created directory `plausible-ce` and verify that the following files exist.

```bash
cd plausible-ce
ls -1
```

This should output the following:

```txt
clickhouse
compose.override.yml
compose.yml
LICENSE
README.md
```

Before you can start the Plausible container the environment and docker compose file need to be set up. First create the secret key base which is used to create the secrets keys your instance uses. Copy the key and create the `.env` file.

```bash
openssl rand -base64 48
nano .env
```
The `.env` contains the base settings for the Plausible instance. Make sure the following four variables are inside your environment file. 

!!! note
    Choosing the port 80/443 enables automatic Let's Encrypt TLS certificate issuance. You can choose different values if you want to run Plausible behind a reverse proxy.

```env
BASE_URL=https://plausible.example.com
SECRET_KEY_BASE=<secretkey>
HTTP_PORT=80
HTTPS_PORT=443
```

!!! warning
    When choosing a domain you want to host your Plausible instance on please be aware that names the contain *analytics* or similar terms are frequently blocked by ad blockers. You can still use for example analytics.example.com without it being blocked by proxying the request on the web server where the Plausible tool is being used on. Plausible offers a straight setup for common proxies [here](https://plausible.io/docs/proxy/introduction).


Now you can configure the compose file. Create the file and edit it.

```bash
nano compose.override.yml
```

Make sure you add the following content to the file, then save it.


```yml
services:
    plausible:
	ports:
            - 80:80
            - 443:443
```

With all preparation done you can start the docker container and login to the website `https://plausible.example.com`.

```bash
sudo docker compose up -d
```

### Setting up Plausible



