# Firewalld Service
Firewalld provides a dynamically managed firewall with support for network/firewall zones that define the trust level of network connections or interfaces. It has support for IPv4, IPv6 firewall settings, ethernet bridges and IP sets. There is a separation of runtime and permanent configuration options. It also provides an interface for services or applications to add firewall rules directly.

<p align="right"><a herf="https://firewalld.org/">firewalld.org</a></p>

## Basic Commands

The service can be configured using the `firewall-cmd` binary. 

|Parameter|Function|Example|
|:-------| :------|---------|
|`--list-all`|List all currently active rules|`firewall-cmd  --list-all`|
|`--reload`|Reloads the firewalld configuration. Easy way to load changed without restarting the service.|`firewall-cmd --reload`|
|`--add-port port/protocol`|Adds the specified port to the ruleset.|`firewall-cmd --add-port=80/tcp --zone=public`|
|`--add-service service`|Adds a predefined or custom service to the ruleset.|`firewall-cmd --add-service=http --zone=public`|
|`--zone=public`|Defines to which zone the rule applies. Default Zone is public.|*|
|`--permanent`|Adds a rule to the permanent rule set. Otherwise the rule will be lost after the next config reload.|`firewall-cmd --add-service=http --zone=public --internal`|

## Creating a custom service
It is best practice to define services to create firewall rules. To create a new service you have to:
1. Navigate to the service directory of firewalld at `/usr/lib/firewalld/services`
2. Copy any given service using **cp** and rename the file to the service of your choosing.
3. Change the port and protocol as well as the description to fit the service youre defining. Your service should look like this example for the AIO interface of Nextcloud

```xml
<?xml version="1.0" encoding="utf-8"?>
    <service>
        <short>NextCloud AIO</short>
        <description>NextCloud AIO Port used to manage the All-In-One NextCloud Containers.</description>
    <port protocol="tcp" port="8443"/>
</service>
```
