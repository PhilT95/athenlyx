# TShark - Basics

> **TShark** is a network protocol analyzer. It lets you capture packet data from a live network, or read packets from a previously saved capture file, either printing a decoded form of those packets to the standard output or writing the packets to a file. TShark's native capture file format is pcapng format, which is also the format used by [Wireshark](../wireshark/wireshark.md) and various other tools.

<p align="right"><a herf="https://www.wireshark.org/docs/man-pages/tshark.html">wireshark.org</a></p>


## Command-Line Packet Analysis

TShark is a text-based tool suitable for data carving, in-depth packet analysis and automation with scripts thanks to being a CLI tool.

??? tip "Capture File details"
    If you want to get details of a specific capture file, you can use the CLI tool `capinfos`

    ```console
    capinfos demo.pcapng
    File name:           demo.pcapng
    File type:           Wireshark/tcpdump/... - pcap
    File encapsulation:  Ethernet
    File timestamp precision:  microseconds (6)
    Packet size limit:   file hdr: 65535 bytes
    Number of packets:   43
    File size:           25 kB
    Data size:           25 kB
    Capture duration:    30.393704 seconds
    First packet time:   2004-05-13 10:17:07.311224
    Last packet time:    2004-05-13 10:17:37.704928
    Data byte rate:      825 bytes/s
    Data bit rate:       6604 bits/s
    Average packet size: 583.51 bytes
    Average packet rate: 1 packets/s
    SHA256:              25a72bdf10339f2c29916920c8b9501d294923108de8f29b19aba7cc001ab60d
    RIPEMD160:           6ef5f0c165a1db4a3cad3116b0c5bcc0cf6b9ab7
    SHA1:                3aac91181c3b7eb34fb7d2b6dd6783f4827fcf07
    Strict time order:   True
    Number of interfaces in file: 1
    Interface #0 info:
                        Encapsulation = Ethernet (1 - ether)
                        Capture length = 65535
                        Time precision = microseconds (6)
                        Time ticks per second = 1000000
                        Number of stat entries = 0
                        Number of packets = 43
    ```

## TShark Fundamentals

### Basic parameters

Understanding and knowing the parameters of TShark is essential. Using the built-in options and associated parameters are needed to keep control of the output and avoid being flooded with the detailed output of TShark.
Some of the most common parameters are:

|Parameter|Description|Example|
|:--------|:----------|:------|
|`-h`|Displays the help page with the most common features.|`tshark -h`|
|`-v`|Shows version info|`tshark -v`|
|`-D`|List available sniffing interfaces|`tshark -D`|
|`-i`|Choose an interface to capture live traffic|`tshark -i 1`<br>`tshark -i ens55`|
|**No parameter**|Sniff the traffic like tcpdump|`tshark`|
|`-r`|Reads a capture file|`tshark -r demo.pcapng`|
|`-c`|Stop after capturing a specified number of packages|`tshark -c 10`|
|`-w`|Write the sniffed traffic to a file|`tshark -w sample-capture.pcap`|
|`-V`|**Verbose** - Provide detailed information for **each packet**|`tshark -V`|
|`-q`|Suppress the packet output on the terminal (silent mode)|`tshark -q`|
|`-x`|Show packet details in Hex and ASCII dump for each packet|`tshark -x`|

### Capture Condition parameters

Since TShark is a network sniffer and packet analyzer, TShark can also be configured to count packets and stop at a specific point or return in a loop structure. The most common parameters for this purpose are:

|Parameter|Description|Example|
|:--------|:----------|:------|
|`-a duration`|Sniff the traffic and stop after a given amount of seconds.|`tshark -w output.pcap -a duration:1`|
|`-a filesize`|Define the maximum capture file size and stop after reaching it (in **KB**)|`tshark -w output.pcap -a filesize:10`|
|`-a files`|Defines the maximum number of output files.|`tshark -w output.pcap -a filesize:10 -a files:3`|

!!! tip "Define capture conditions for multiple runs/loops"
    If you replace `-a` with the `-b` parameter using the same syntax, you can run these commands in an **Infinite Loop**. You need to use at least one *autostop* (`-a`) parameter if you want to stop the infinite loop.

!!! note
    You can only use these capture condition parameters while TShark is in *capture/sniffing* mode. 

## Capture & Display filters

TShark, like other tools, can be used to filter **live (capture)** and *display **(post-capture)** data. These 2 dimensions can be filtered with 2 different approaches:

- Predefined Syntax
- BPF

TShark supports both, so you can use Wireshark filters and BPF to filter traffic. TShark, being the CLI version of Wireshark, also uses **Capture** and **Display Filters**.(1)
{ .annotate }

1. You can read more about these filters in [Wireshark](../wireshark/wireshark.md#package-filtering).

Capture filters have limited filtering features, and the purpose is to implement a scope by range, protocol and direction filtering. They can be used to limit file size and focus on important traffic. Display filters investigate the capture files in-depth without modifying the packet.

|Parameter|Description|
|:--------|:----------|
|`-f`|Capture filters using the syntax as BPF and Wireshark's capture filter|
|`-Y`|Display filters using the same syntax as Wireshark's display filters|

### Capture Filters

TShark uses Wireshark's capture filter syntax here. Below are a few examples, but if you want to read more, you can visit [Wireshark.org](https://www.wireshark.org/docs/man-pages/pcap-filter.html) or [WireShark GitLab](https://gitlab.com/wireshark/wireshark/-/wikis/CaptureFilters#useful-filters).

|Qualifier|Details and Available Options|Examples|
|:--------|:----------------------------|:-------|
|**Type**|You can filter IP addresses, host names, IP ranges  and port numbers. If you don't set a qualifier, the *host* qualifier will be used by default.|Filtering a host<br>`tshark -f "host 10.0.0.10"`|
|||Filtering a network range<br>`tshark -f "net 10.0.10.0/24"`|
|||Filtering a port<br>`tshark -f "port 80"`|
|||Filtering a port range<br>`tshark -f "portrange 80-100"`|
|**Direction**|Filter for the target direction/flow. If you don't use the direction operator, it will be equal to *either* and cover both directions.|Filtering source address<br>`tshark -f "src host 10.10.0.10"`|
|||Filtering destination address<br>`tshark -f "dst host 10.10.0.10"`|
|**Protocol**|Filter for the protocol.|Filtering TCP<br>`tshark -f "tcp"`|
|||Filtering MAC address<br>`tshark -f "ether host F8:D8:C6:A3:5D:81"`|
|||You can also filter protocols with IP protocol number assigned by IANA<br>`tshark -f "ip proto 1"`|

### Display Filters

TShark also uses Wireshark's syntax here. You can use the [official documentation](https://www.wireshark.org/docs/dfref/) or use WireShark's built-in **Display Filter Expression** menu. Some common filtering option are below.

!!! note
    Using single quotes for capture filters is recommended to avoid space and bash expansion problems. You can also refer to the [Wireshark Advanced Features Guide](../wireshark/wireshark_advanced.md).

|Display Filter Category|Examples|
|:----------------------|:-------|
|**Protocol:  IP**|Filtering an IP without specifying a direction<br>`tshark -Y 'ip.addr == 10.0.0.10'`|
||Filtering a network range<br>`tshark -Y 'ip.addr == 10.0.0.10/24'`|
||Filtering a source IP<br>`tshark -Y 'ip.src == 10.0.0.10'`|
||Filtering a destination IP<br>`tshark -Y 'ip.dst == 10.0.0.10'`|
|**Protocol:  TCP**|Filter TCP Port<br>`tshark -Y 'tcp.port == 80'`|
||Filter TCP source Port<br>`tshark -Y 'tcp.srcport == 80'`|
|**Protocol:  HTTP**|Filter HTTP Packets<br>`tshark -Y 'http'`|
||Filter HTTP Packets with response code **200**<br>`tshark -Y 'http.response.code == 200'`|
|**Protocol:  DNS**|Filter DNS packets<br>`tshark -Y 'dns'`|
||Filter all DNS **A** packets<br>`tshark -Y 'dns.qry.type == 1'`|





