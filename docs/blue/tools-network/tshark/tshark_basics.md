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
