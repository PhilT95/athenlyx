# Wireshark - Traffic analysis

Using the knowledge from [Wireshark Basics](wireshark.md) and [Wireshark - Advanced Features](wireshark_advanced.md) you can now investigate anmd correlate packet-level information and start seeing the big picture behind in network traffic like detectin anomalies and malicious activities.

## Detecting Nmap scans

Nmap is a very commonly used tool for mapping networks, identifying live hosts and discovering services. But it also leaves a pattern which can be detected. The most common Nmap scan types are:

- TCP connect status
- SYN scans
- UPD scans

To be able to detect Nmaps activity, you need to understand its scan behavior on the network.

### TCP flags summary

|Notes|Wireshark filters|
|:----|:----------------|
|Global search|<ul><li>`tcp`</li><li>`udp`</li></ul>|
|<ul><li>Only SYN flag</li><li>SYN flag is set. The rest of the bits are not important.</li></ul>|<ul><li>`tcp.flags == 2`</li><li>`tcp.flags.syn == 1`</li></ul>|
|<ul><li>Only ACK flag</li><li>ACK flag is set. The rest of the bits are not important.</li></ul>|<ul><li>`tcp.flags == 16`</li><li>`tcp.flags.ack == 1`</li></ul>|
|<ul><li>Only SYN, ACK flags</li><li>SYN and ACK flag are set. The rest of the bits are not important.</li></ul>|<ul><li>`tcp.flags == 18`</li><li>`(tcp.flags.syn == 1) and (tcp.flags.ack == 1)`</li></ul>|
|<ul><li>Only RST flag</li><li>RST flag is set. The rest of the bits are not important.</li></ul>|<ul><li>`tcp.flags == 4`</li><li>`tcp.flags.reset == 1`</li></ul>|
|<ul><li>Only RST, ACK flags</li><li>RST and ACK flag are set. The rest of the bits are not important.</li></ul>|<ul><li>`tcp.flags == 20`</li><li>`(tcp.flags.reset == 1) and (tcp.flags.ack == 1)`</li></ul>|
|<ul><li>Only FIN flag</li><li>FIN flag is set. The rest of the bits are not important.</li></ul>|<ul><li>`tcp.flags == 1`</li><li>`tcp.flags.fin == 1`</li></ul>|

### TCP Connect Scans

The TCP Connect scan:

- Relies on the three-way handshake
- Usually conducted with the `nmap -sT` command
- Usually run by non-privileged users
- Usually has a windows size larger than **1024 bytes** as the request expects some data due to the nature of the protocol

|Open TCP Port|Open TCP Port|Closed TCP Port|
|:------------|:------------|:--------------|
|<ul><li>SYN -></li><li><- SYN,ACK</li><li>ACK -></li></ul>|<ul><li>SYN -></li><li><- SYN,ACK</li><li>ACK -></li><li>RST,ACK -></li></ul>|<ul><li>SYN -></li><li><- RST,ACK</li></ul>|

!!! example "Example Filter for TCP Connect Scans"
    `tcp.flags.syn==1 and tcp.flags.ack==0 and tcp.windows_size > 1024`

### SYN Scans

The TCP SYN scan:

- Doesn't rely on the three-way handshake
- Usually conducted with the `nmap -sS` command
- Usually by privileged users
- Usually have a size less than or equal to **1024** bytes as the request is not finished and it doesn't expect to receive data.
- 
|Open TCP Port|Close TCP Port|
|:------------|:-------------|
|<ul><li>SYN -></li><li><- SYN,ACK</li><li>RST -></li></ul>|<ul><li>SYN -></li><li><- RST,ACK</li></ul>|

!!! example "Example Filter for SYN Scans"
    `tcp.flags.syn==1 and tcp.flags.ack==0 and tcp.window_size <= 1024`


### UDP Scans

The UDP Scan:

- Doesn't require a handshake process
- No prompt for open ports
- ICMP error message for close ports
- Usually conducted with the `nmap -sU` command

|Open UDP Port|Close UDP Port|
|:------------|:-------------|
|<ul><li>UDP packet -></li></ul>|<ul><li>UDP packet -></li><li>ICMP Type 3, Code 3 message (Destination unreachable, port unreachable)</li></ul>|

!!! example "Example Filter for UDP Scans"
    `icmp.type==3 and icmp.code==3`


## ARP Poisoning/Spoofing


!!! Quote "What is ARP?"
    The ARP is a communication protocol for discovering the link layer address, such as a MAC address, associated with a internet layer address, typically an IPv4 address.

<p align="right"><a herf="https://en.wikipedia.org/wiki/Address_Resolution_Protocol">Wikipedia.org</a></p>

ARP Poisoning, also known as ARP Spoofing or Man in the Middle attack, is a type of attack that involves network jamming/manipulating by sending malicious ARP packets to the default gateway. The goal of this attack is to manipulate the **IP to MAC address table** and sniff the traffic of the target host.

ARP analysis boils down to:

- Work on the local network
- Enables the communication between MAC addresses
- Not a secure protocol
- Not a routable protocol
- It doesn't have an authentication function
- Common patterns are:

    - Request and response
    - Announcement and gratuitous packets

|Notes|Wireshark filter|
|:----|:---------------|
|Global search|`arp`|
|Opcode 1: ARP requests|`arp.opcode == 1`|
|Opcode 2: ARP responses|`arp.opcode == 2`|
|**Hunt**: ARP scanning|`arp.dst.hw_mac==00:00:00:00:00:00`|
|**Hunt**: Possible ARP poisoning detection|`arp.duplicate-address-detected or arp.duplicate-address-frame`|
|**Hunt**: Possible ARP flooding from detection|`((arp) && (arp.opcode == 1)) && (arp.src.hw_mac == target-mac-address)`|

A suspicious situation means having two different ARP responses (conflict) for a particular IP address. Wireshark alerts you, but it only shows the second occurrence of the duplicate value to highlight the conflict. Identifying the malicious packet from the legitimate one is your challenge.

## Identifying Hosts

When investigating a compromise or malware infection, you should know how to identify the host on the network apart from IP to MAC address match. One way to to di is identifying the host and users on the network to decide the investigation's starting point and list the hosts and users associated with the malicious traffic/activity. These protocols can be used in Host and user identification:

- DHCP traffic
- NetBIOS traffic
- Kerberos traffic

### DHCP Analysis

DHCP is used to automatically manage OP addresses and their assignments.

|Notes|Wireshark filter|
|:----|:---------------|
|Global search|`dhcp` or `bootp`|
|**DHCP Request** packets contain the hostname information|`dhcp.option.dhcp == 3`|
|**DHCP ACK** packets represent the accepted requests|`dhcp.option.dhcp == 5`|
|**DHCP NAK** packets represent denied requests|`dhcp.option.dhcp == 6`|
|**DHCP Request** can be filteres for the following options <ul><li>**Option 12**: Hostname</li><li>**Option 50**: Requested IP address</li><li>**Option 51**: Requested IP lease time</li><li>**Option 61**: Client's MAC address</li></ul>|`dhcp.option.hostname contains "keyword"`|
|**DHCP ACK** options: <ul><li>**Option 15**: Domain name</li><li>**Option 51**: Assigned IP lease time</li></ul>|`dhcp.otion.domain_name contains "keyword"`|
|**DHCP NAK** options: <ul><li>**Option 56**: Message (rejection details/reason)</li></ul>|Since the message could be unique to the situation, it is suggested to read the message instead of filtering it.|

??? info "Option 53"
    Due to the nature of the protocol, only **Option 53** (request type) has predefined static values. You should filter the packet type first and then you can filter the rest of the options by either using **applying as column** or us the advanced filters like **contains** or **matches**.

!!! tip "Accessing Options"
    The Options are part of the packet details and filtering depends on the protocol. Inspect the specific protocol and you will see the option. Just set a filter using the **Apply Filter** menu and you can modify the query further yourself!

### NetBIOS Analysis

NetBIOS is responisble for allowing applications on different hosts to communicate with each other.

|Notes|Wireshark filter|
|:----|:---------------|
|Global search|`nbns`|
|**NBNS** options is **Queries**, which are filters for Query details and can contain:<ul><li>**name**</li><li>**TTL**</li><li>**IP address details**</li></ul>|`nbns.name contains ""keyword"`|

### Kerberos Analysis

Kerberos is the default authentication service within Microsoft Windows domains. It is responsible for authenticating service requests between 2 or more computers over the untrusted network. The goal is to prove identiy securely.

|Notes|Wireshark filter|
|:----|:---------------|
|Global search|`kerberos`|
|User account search using **CNameString**, which is the username|<ul><li>`kerberos.CNameString contains "keyword"`</li><li>`kerberos.CNameString and !(kerberos.CNameString contains "$")`</li></ul>|
|**pvno**: Protocol version|`kerberos.pvno == 5`|
|**realm**: Domain name for the generated ticket|`kerberos.realm contains ".org"`|
|**sname**: Service and domain name for the generated ticket|`kerberos.SNameString == "krbtg"`|
|**addresses**: Client IP address and NetBIOS name|`kerberos.addresses`|

!!! note 
    The **addresses* information is only available in request packets.

??? info "User Account search confusion"
    Some packets could provide hostname information in the **CNameString** field. To avoid this confusion, filter the **\$** value. The values end with **\$** are hostnames, the ones without it are user names.


## Tunneling Traffic

Traffic tunenling, also known as **port forwarding** is a way to transfer data in a secure method to segments and zones. It can be used for *internet to private networks* flows. There is an encapsulation process to hide the data so the transferred data appears natural, but it contains private data packets and transfers them to the final destination securely.  
Tunneling provides anonymity and security and is therefore used by enterprise networks. However, this level of data encryption also makes it a method for attackers to bypass security perimeters using the standard and trusted protocols used in everyday traffic like ICMP and DNS.

### ICMP Analysis

ICMP is designed for diagnosing and reporting network communication issues. It is a trusted network layer protocol and also sometimes used for DoS attacks. It is also used in data exfiltration and C2 tunneling activities.

Usually ICMP tunneling attacks are anomalies appearing after a malware execution or vulnerability exploitation. As the ICMP packet can transfer additional data payloads, it can be used to exfiltrate data and establish a C2 connection. Within the ICMP traffic could be TCP, HTTP or SSH data. Most of the time, these custom ICMP packets are blocked by default, but adversaries can match these default packets.

|Notes|Wireshark filter|
|:----|:---------------|
|Global search|`icmp`|
|Packet length|`data.len > 64 and icmp`|
|ICMP destination address||
|Encapsulated protocol signs in ICMP payload||

### DNS Analysis

DNS is designed to translate domain names to IP addresses. It is a very crucial part for web services and the Internet in general. It is very commonly used and trusted and therefore often ignored. Like [ICMP](#icmp-analysis), it is also used for data exfiltration and C2 activities.

Similar to ICMP tunnels, DNS attacks are anomalies that appear after a malware execution or vulnerability exploitation. Domain addresses can be created and configured as a C2 channel. The commands or malware sends DNS queries to the C2 server. However, these queries are longer than default queries and crafted for subdomain addresses. These addresses are not real and used to encode commands like  

**encoded-commands.example.org**

When this query is routed to the C2 server, the server sends the actual malicious commands to the host.

|Notes|Wireshark filter|
|:----|:---------------|
|Global search|`dns`|
|Query length|`dns.qry.name.len`|
|Long DNS addresses with encoded subdomain addresses|`dns.qry.len > 15`|
|Kown patterns like dnscat and dns2tcp|`dns contains "dnscat"`|
|**!mdns**: Disable local link device queries|`dns.qry.name.len > 15 and !mdns`|


## Cleartext Protocol Analysis

### FTP Analysis

FTP is designed to transfer files easily. With its simplicity comes a lack of security. THis protocol should not be used in unsecured environments because it creates risks like:

- Man-in-the-middle attacks
- Credential stealing and unauthorized access
- Phishing
- Malware planting
- Data exfiltration

|Notes|Wireshark filter|
|:----|:---------------|
|Global search|`ftp`|
|**FTP option 211**: System status|`ftp.response.code == 211`|
|**FTP option 212**: Directory status|`ftp.response.code == 212`|
|**FTP option 213**: File status|`ftp.response.code == 213`|
|**FTP option 220**: Service ready|`ftp.response.code == 220`|
|**FTP option 227**: Entering passive mode|`ftp.response.code == 227`|
|**FTP option 228**: Long passive mode|`ftp.response.code == 228`|
|**FTP option 229**: Extended passive mode|`ftp.response.code == 229`
|**FTP option 230**: User login|`ftp.response.code == 230`|
|**FTP option 231**: User logout|`ftp.response.code == 231`|
|**FTP option 331**: Valid username|`ftp.response.code == 331`|
|**FTP option 430**: Invalid username or password|`ftp.response.code == 430`|
|**FTP option 530**: No login, invalid password|`ftp.response.code == 530`|
|**USER**: Username|`ftp.request.command == "USER"`|
|**PASS**: Password|`ftp.request.command == "PASS"`|
|**Bruteforce signal**: List failed login attempts|`ftp.response.code == 530`|
|**Bruteforce signal**: List target username|`(ftp.response.code == 530) and (ftp.response.arg contains "username")`|
|**Password spray signal**: List targets for a static password|`(ftp.response.command == "PASS") and (ftp.request.arg == "password")`|

!!! tip
    You can use the *Follow TCP* option to see more details from a packet with the response code **213**.



