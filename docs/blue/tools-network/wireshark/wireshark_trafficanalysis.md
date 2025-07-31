# Wireshark - Traffic analysis

Using the knowledge from [Wireshark Basics](wireshark.md) and [Wireshark - Advanced Features](wireshark_advanced.md) you can now investigate anmd correlate packet-level information and start seeing the big picture behind in network traffic like detectin anomalies and malicious activities.

## Detectin Nmap scans

Nmap is a very commonly used tool for mapping networks, identifying live hosts and discovering services. But it also leaves a pattern which can be detected. The most common Nmap scan types are:

- TCP connect status
- SYN scans
- UPD scans

To be able to detect Nmaps activity, you need to understand its scan behaviour on the network.

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

ARP Poisoning, also known as ARP Spoofing or Man in the Middle attack, is a type of attack that involves network jamming/manipulating by sending malivous ARP packets to the default gateway. The goal of this attack is to manipulate the **IP to MAC address table** and sniff the traffic of the target host.

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