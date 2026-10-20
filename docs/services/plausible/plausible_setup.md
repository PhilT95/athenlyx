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

This will ensure that the system is fully up to date. If required reboot the system and log in again once it is up.

### Installing prerequisites

Since the installation requires Docker, please refer to the [AlmaLinux 10 Setup Guide](../../infra-mgmt/linux-admin/rhel-alma/almalinux_setup.md#installing-docker) for these steps. Once you are done with the docker installation the only needed prerequisite left is git.

```bash
sudo dnf install git -y
```

### Installing Plausible

