# TShark CLI Wireshark Features

## Statistics

As explained in [TShark Basics](./tshark_basics.md), it is considered the CLI version of Wireshark. That means that TShark can accomplish several features of Wireshark.

!!! note
    The following options apply to all packets in scope unless a *Display Filter* is provided. 

|Parameters|Description|Example|
|:---------|:----------|:------|
|`--color`|Wireshark-like colorized output|`tshark --color`|
|`-z`|Shows statistics. The parameters offers multiple options which can be viewed using `tshark -z help`. You can suppress the packets and focus on the statistics using the `-q` parameter. |`tshark -z filter`|

Some interesting statistics options are:

|Statistics option|Function|
|:----------------|:-------|
|`-z plen,tree`|Shows the package length by size in a tree format
|`-z io,phs`|Shows the protocol hierarchy|
|`-z io,phs,udp`|Filters the protocol hierarchy for UDP packages|
|`-z endpoints,ip`|Providing a summarized view of the endpoints by IPv4 addresses|
|`-z endpoints,eth`|Providing a summarized view of the endpoints by Ethernet addresses|
|`-z endpoints,ipv6`|Providing a summarized view of the endpoints by IPv6 addresses|
|`-z endpoints,tcp`|Providing a summarized view of the endpoints by TCP addresses. Works for IPv4 and IPv6.|
|`-z endpoints,udp`|Providing a summarized view of the endpoints by UDP addresses. Works for IPv4 and IPv6.|
|`-z endpoints,wlan`|Providing a summarized view of the endpoints by IEEE 802.11 addresses|

A few mre interesting statistics are:

- `-z conv` : This view provides an overview of the traffic flow between to particual connection points. Similar to the endpoint filtering, conversations can be viewed in multiple formats like `-z conv,ip`
- `-z expert`: This view helps you to view automatic comments provided by Wireshark. 

!!! tip "Focusing on the statistics"
    Don't forget to use the `-q` parameter to suppress the packets themselves and focus on the statistics you want to see like `tshark -r test.pcap -z expert -q`



```console title="TShark Statistics Example"
user@host: ~$ tshark -r demo.pcapng -z conv,ip -q
================================================================================
IPv4 Conversations
Filter:<No Filter>
                                               |       <-      | |       ->      | |     Total     |    Relative    |   Duration   |
                                               | Frames  Bytes | | Frames  Bytes | | Frames  Bytes |      Start     |              |
65.208.228.223       <-> 145.254.160.237           16      1351      18     19344      34     20695     0.000000000        30.3937
145.254.160.237      <-> 216.239.59.99              4      3236       3       883       7      4119     2.984291000         1.7926
145.253.2.203        <-> 145.254.160.237            1        89       1       188       2       277     2.553672000         0.3605
================================================================================
```

### IPv4 and IPv6 Statistics

This option provides statistics on IPv4 and IPv6 packets. Having these protocol statistics helps you to overview distribution according to the protocol type. You can filter available protocol types and view the details using `-z ptype,tree -q`

```console
user@host: ~$ tshark -r demo.pcapng -z ptype,tree -q

==================================================================================================================================
IPv4 Statistics/IP Protocol Types:
Topic / Item       Count         Average       Min val       Max val       Rate (ms)     Percent       Burst rate    Burst start  
----------------------------------------------------------------------------------------------------------------------------------
IP Protocol Types  43                                                      0.0014        100%          0.0400        2.554        
 TCP               41                                                      0.0013        95.35%        0.0300        0.911        
 UDP               2                                                       0.0001        4.65%         0.0100        2.554        

----------------------------------------------------------------------------------------------------------------------------------
```

You can also create a summary of the hosts in a single view. You can filter all IP addresses using these parameters:

- **IPv4**: `-z ip_hosts,tree -q`
- **IPv6**: `-z ipv6_hosts,tree -q`

```console
user@host: ~$ tshark -r demo.pcapng -z ip_hosts,tree -q

=================================================================================================================================
IPv4 Statistics/All Addresses:
Topic / Item      Count         Average       Min val       Max val       Rate (ms)     Percent       Burst rate    Burst start  
---------------------------------------------------------------------------------------------------------------------------------
All Addresses     43                                                      0.0014        100%          0.0400        2.554        
 145.254.160.237  43                                                      0.0014        100.00%       0.0400        2.554        
 65.208.228.223   34                                                      0.0011        79.07%        0.0300        0.911        
 216.239.59.99    7                                                       0.0002        16.28%        0.0300        3.916        
 145.253.2.203    2                                                       0.0001        4.65%         0.0100        2.554        

---------------------------------------------------------------------------------------------------------------------------------
```

For a more in-depth analysis, you need to correlate the finding by focusing on the source and destination address. You can filter these by using the following parameters:

- **IPv4**: `-z ip_srcdst, tree -q`
- **IPv6**: `-z ipv6_srcdst, tree -q`

```console
user@host: ~$ tshark -r demo.pcapng -z ip_srcdst,tree -q

================================================================================================================================================
IPv4 Statistics/Source and Destination Addresses:
Topic / Item                     Count         Average       Min val       Max val       Rate (ms)     Percent       Burst rate    Burst start  
------------------------------------------------------------------------------------------------------------------------------------------------
Source IPv4 Addresses            43                                                      0.0014        100%          0.0400        2.554        
 145.254.160.237                 20                                                      0.0007        46.51%        0.0200        0.911        
 65.208.228.223                  18                                                      0.0006        41.86%        0.0200        2.554        
 216.239.59.99                   4                                                       0.0001        9.30%         0.0200        3.916        
 145.253.2.203                   1                                                       0.0000        2.33%         0.0100        2.914        
Destination IPv4 Addresses       43                                                      0.0014        100%          0.0400        2.554        
 145.254.160.237                 23                                                      0.0008        53.49%        0.0200        2.554        
 65.208.228.223                  16                                                      0.0005        37.21%        0.0200        0.911        
 216.239.59.99                   3                                                       0.0001        6.98%         0.0100        2.984        
 145.253.2.203                   1                                                       0.0000        2.33%         0.0100        2.554        

------------------------------------------------------------------------------------------------------------------------------------------------
```

In some cases you will need to focus on the outgoing traffic to spot used services and ports. This can be achieved using these parameters:

- **IPv4**: `-z dests,tree -q`
- **IPv6**: `-z ipv6_dests,tree -q`

```console
user@host: ~$ tshark -r demo.pcapng -z dests,tree -q

=======================================================================================================================================
IPv4 Statistics/Destinations and Ports:
Topic / Item            Count         Average       Min val       Max val       Rate (ms)     Percent       Burst rate    Burst start  
---------------------------------------------------------------------------------------------------------------------------------------
Destinations and Ports  43                                                      0.0014        100%          0.0400        2.554        
 145.254.160.237        23                                                      0.0008        53.49%        0.0200        2.554        
  TCP                   22                                                      0.0007        95.65%        0.0200        2.554        
   3372                 18                                                      0.0006        81.82%        0.0200        2.554        
   3371                 4                                                       0.0001        18.18%        0.0200        3.916        
  UDP                   1                                                       0.0000        4.35%         0.0100        2.914        
   3009                 1                                                       0.0000        100.00%       0.0100        2.914        
 65.208.228.223         16                                                      0.0005        37.21%        0.0200        0.911        
  TCP                   16                                                      0.0005        100.00%       0.0200        0.911        
   80                   16                                                      0.0005        100.00%       0.0200        0.911        
 216.239.59.99          3                                                       0.0001        6.98%         0.0100        2.984        
  TCP                   3                                                       0.0001        100.00%       0.0100        2.984        
   80                   3                                                       0.0001        100.00%       0.0100        2.984        
 145.253.2.203          1                                                       0.0000        2.33%         0.0100        2.554        
  UDP                   1                                                       0.0000        100.00%       0.0100        2.554        
   53                   1                                                       0.0000        100.00%       0.0100        2.554        

---------------------------------------------------------------------------------------------------------------------------------------
```

### DNS Statistics

This option provides statistics on DNS packets by summarizing available information. You can filter the packets and view the details using the `-z dns,tree -q` parameters.

```console
user@host: ~$ tshark -r demo.pcapng -z dns,tree -q

==============================================================================================================================================
DNS:
Topic / Item                   Count         Average       Min val       Max val       Rate (ms)     Percent       Burst rate    Burst start  
----------------------------------------------------------------------------------------------------------------------------------------------
Total Packets                  2                                                       0.0055        100%          0.0100        2.554        
 rcode                         2                                                       0.0055        100.00%       0.0100        2.554        
  No error                     2                                                       0.0055        100.00%       0.0100        2.554        
 opcodes                       2                                                       0.0055        100.00%       0.0100        2.554        
  Standard query               2                                                       0.0055        100.00%       0.0100        2.554        
 Query/Response                2                                                       0.0055        100.00%       0.0100        2.554        
  Response                     1                                                       0.0028        50.00%        0.0100        2.914        
  Query                        1                                                       0.0028        50.00%        0.0100        2.554        
 Query Type                    2                                                       0.0055        100.00%       0.0100        2.554        
  A (Host Address)             2                                                       0.0055        100.00%       0.0100        2.554        
 Class                         2                                                       0.0055        100.00%       0.0100        2.554        
  IN                           2                                                       0.0055        100.00%       0.0100        2.554        
Payload size                   2             96.50         47            146           0.0055        100%          0.0100        2.554        
Query Stats                    0                                                       0.0000        100%          -             -            
 Qname Len                     1             29.00         29            29            0.0028                      0.0100        2.554        
 Label Stats                   0                                                       0.0000                      -             -            
  3rd Level                    1                                                       0.0028                      0.0100        2.554        
  4th Level or more            0                                                       0.0000                      -             -            
  2nd Level                    0                                                       0.0000                      -             -            
  1st Level                    0                                                       0.0000                      -             -            
Response Stats                 0                                                       0.0000        100%          -             -            
 no. of questions              2             1.00          1             1             0.0055                      0.0200        2.914        
 no. of authorities            2             0.00          0             0             0.0055                      0.0200        2.914        
 no. of answers                2             4.00          4             4             0.0055                      0.0200        2.914        
 no. of additionals            2             0.00          0             0             0.0055                      0.0200        2.914        
Service Stats                  0                                                       0.0000        100%          -             -            
 request-response time (secs)  1             0.36          0.360518      0.360518      0.0028                      0.0100        2.914        
 no. of unsolicited responses  0                                                       0.0000                      -             -            
 no. of retransmissions        0                                                       0.0000                      -             -            

----------------------------------------------------------------------------------------------------------------------------------------------
```

### HTTP Statistics

This option provides statistics on HTTP packets by summarizing load distribution, requests, packets and status info. You can filter the packets with the following parameters:

- **Packet and status counter for HTTP**: `-z http,tree -q`
- **Packet and status counter for HTTP2**: `-z http2,tree -q`
- **Load distribution**: `-z http_srv,tree -q`
- **Requests**: `-z http_req,tree -q`
- **Requests and responses**: `-z http_seq,tree -q`

```console
user@host: ~$ tshark -r demo.pcapng -z http,tree -q

=======================================================================================================================================
HTTP/Packet Counter:
Topic / Item            Count         Average       Min val       Max val       Rate (ms)     Percent       Burst rate    Burst start  
---------------------------------------------------------------------------------------------------------------------------------------
Total HTTP Packets      4                                                       0.0010        100%          0.0100        0.911        
 HTTP Response Packets  2                                                       0.0005        50.00%        0.0100        3.956        
  2xx: Success          2                                                       0.0005        100.00%       0.0100        3.956        
   200 OK               2                                                       0.0005        100.00%       0.0100        3.956        
  ???: broken           0                                                       0.0000        0.00%         -             -            
  5xx: Server Error     0                                                       0.0000        0.00%         -             -            
  4xx: Client Error     0                                                       0.0000        0.00%         -             -            
  3xx: Redirection      0                                                       0.0000        0.00%         -             -            
  1xx: Informational    0                                                       0.0000        0.00%         -             -            
 HTTP Request Packets   2                                                       0.0005        50.00%        0.0100        0.911        
  GET                   2                                                       0.0005        100.00%       0.0100        0.911        
 Other HTTP Packets     0                                                       0.0000        0.00%         -             -            

---------------------------------------------------------------------------------------------------------------------------------------
```
