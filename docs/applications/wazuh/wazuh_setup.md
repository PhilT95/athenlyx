# Installing Wazuh on Almalinux 10 - Quickstart Guide

The **Wazuh** server consists of 3 components:

- Wazuh indexer
- Wazuh server
- Wazuh dashboard

These components can be installed on different and on the same machine alike. This guide focuses on the installation on the same machine. For more complex and demanding workloads it is recommended to provide separate servers for the components.

## Requirements

Wazuh itself recommends the following hardware capabilities depending on the amount of agents:

|Agents|CPU|RAM|Storage for 90 days|
|:-----|:--|:--|:------------------|
|1-25|4 vCPU|8 GiB|50 GB|
|25-50|8 vCPU|8 GiB|100 GB|
|50-100|8vCPU|8 GiB|200 GB|

!!! note
    For very small setups (homelab etc.) less RAM can be used.

## Installation Process

Wazuh offers an *Installation assistant* that completely deploys all requirements and installs the essentials components of Wazuh.


```bash-session
[root@wazuh user]# curl -sO https://packages.wazuh.com/4.12/wazuh-install.sh && sudo bash ./wazuh-install.sh -a
```

Once the installation assistant finishes the installation, the console will display the web interface as well as the default user and password.

```bash-session
INFO: --- Summary ---
INFO: You can access the web interface https://<WAZUH_DASHBOARD_IP_ADDRESS>
    User: admin
    Password: <ADMIN_PASSWORD>
INFO: Installation finished.
```