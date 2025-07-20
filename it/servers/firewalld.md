# Firewalld Service
Firewalld provides a dynamically managed firewall with support for network/firewall zones that define the trust level of network connections or interfaces. It has support for IPv4, IPv6 firewall settings, ethernet bridges and IP sets. There is a separation of runtime and permanent configuration options. It also provides an interface for services or applications to add firewall rules directly.

<p align="right"><a herf="https://firewalld.org/">firewalld.org</a></p>

## Basic Commands

The service can be configured using the `firewall-cmd` binary. 

|Parameter|Function|Example|
|:-------| :------|---------|
|`--list-all`|List all currently active rules|`firewall-cmd  --list-all`|
|`--reload`|Reloads the firewalld configuration. Easy way to load changed without restarting the service.|`firewall-cmd --reload`|
