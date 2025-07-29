# Wireshark - Advanced Features

## Statistics

The statistics menu provides multiple statistics options to investigate and help users see the big picture regarding the scope of the traffic, available protocols, endpoints and conversations as well as some protocol-specific details like DHCP, DNS and HTTP. 

### Resolve Addresses

Resolving addresses helps to identify addresses and DNS names available in the capture files by providing the list of the resolved addresses and their hostnames. You can quickly identify accessed resources by using this menu and evaluate these ressources according to the event. This option is available through the **Statistics --> Resolved Addresses** menu.

![Image](images/wireshark-advanced_resolved.png)


!!! tip
    Select *Hosts* like in the picture above to filter correctly.

### Protocol Hierarchy

This can be used to break down all available protocols from the capture file and provided a tree view based look into the protocols regarding packet counters and percentages. 

![Image](images/wireshark-advanced_hierarchy.png)

!!! tip
    You can **right-click** within this menu to filter specific events.

### Conversations

A conversation represents traffic between to specific endpoints. This option provides the list of the conversation in 5 base formats:

1. Ethernet
2. IPv4
3. IPv6
4. TCP
5. UDP

You can access this menu via **Statistics --> Conversations**.

![Image](images/wireshark-advanced_conversations.png)

### Endpoints

The endpoints option is similar to the [Conversations](#conversations) option. The difference between the two is that endpoints provides unique information for a single information field (Ethernet, IPv4, IPv6, TCP and UDP). This can be accessed via the **Statistics --> Endpoints** menu.
Wireshark also supports resolving MAC addresses into human-readable format using the manufacturer that is assigned by the IEEE. This only works for the *known* manufacturers.

![Image](images/wireshark-advanced_endpoints.png)

The name resolution is not limited to only MAC addresses. Wireshark also offers IP and port name resolution options as well, altough these options are not enabled by default. You can access these settings via the **Edit --> Preferences --> Name Resolution** menu.

![Image](images/wireshark-advanced_nameresolution.png)

Additionally, Wireshark also provides an IP geolocation mapping to identify the geolocation of source and destination addresses. This feature is also not enabled by default and needs additional data from services like the GeoIP database. Wireshark currently supports MaxMind databases and the lastest version comes configured with a MaxMind DB resolver. You still need to provide the DB files and provide this database to Wireshark using **Edit --> Preferences --> Name Resolution --> MaxMind database directories**.

### IPv4 and IPv6

Until now, almost all options provided information that contained both IPv4 and IPv6. The statistics menu has 2 options to narrow down the statistics on packets containig a specific IP version. This way you can identify and list all events linked to specific IP versions in a single windows. This can be accessed via the **Statistics --> IPvX Statistics** menu.

![Image](images/wireshark-advanced_ipvx.png)

### DNS

Wireshark offers an option to break down all DNS packets from the capture file and provides the findings in a tree view based on packet counters and percentages of the DNS protocol. You can use this to view the DNS overall usage, including:

- rcode
- opcode
- class
- query type
- service
- query stats

This option can be accessed via the **Statistics --> DNS** menu.

![Image](images/wireshark-advanced_dns.png)

### HTTP

This function breaks down all HTTP packets from the capture file and helps to view the findings in a tree view based on packet counters and percentages of the HTTP protocol. You cann access this via the **Statistics --> HTTP** menu.

![Image](images/wireshark-advanced_http.png)

!!! tip
    Don't forget to scroll sideways within this windows!

## Packet Filtering