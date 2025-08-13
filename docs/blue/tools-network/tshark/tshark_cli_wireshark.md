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
user@host:~$ tshark -r demo.pcapng -z conv,ip -q
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
user@host:~$ tshark -r demo.pcapng -z ptype,tree -q

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
user@host:~$ tshark -r demo.pcapng -z ip_hosts,tree -q

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
user@host:~$ tshark -r demo.pcapng -z ip_srcdst,tree -q

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
user@host:~$ tshark -r demo.pcapng -z dests,tree -q

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
user@host:~$ tshark -r demo.pcapng -z dns,tree -q

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
user@host:~$ tshark -r demo.pcapng -z http,tree -q

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

## Streams, Objects and Credentials

A lot of filters are designed for multiple purposes. The most common filtering operations are described below.

!!! note
    Most of these commands are CLI versions of the corresponding Wireshark features.

### Follow Stream

**Follow Stream** helps to follow traffic streams similar to [Wireshark](../wireshark/wireshark_trafficanalysis.md). The query structure words with the following parameters

- **Main Parameter and protocol**: `-z follow,tcp`
- **View Mode**: Can be set to *ASCII* or *HEX*
- **Stream Number**: Stream starts from *0*.

To filter the packets and follow a TCP stream, you use the query `-z follow,tcp,ascii,0 -q`

!!! tip
    You can exchange `-z follow,tcp,...` for `-z follow,udp` or `-z follow,http` to filter for **UDP** or **HTTP** streams

```console
user@host:~$ tshark -r demo.pcapng -z follow,tcp,ascii,1 -q

===================================================================
Follow: tcp,ascii
Filter: tcp.stream eq 1
Node 0: 145.254.160.237:3371
Node 1: 216.239.59.99:80
721
GET /pagead/ads?client=ca-pub-2309191948673629&random=1084443430285&lmt=1082467020&format=468x60_as&output=html&url=http%3A%2F%2Fwww.ethereal.com%2Fdownload.html&color_bg=FFFFFF&color_text=333333&color_link=000000&color_url=666633&color_border=666633 HTTP/1.1
Host: pagead2.googlesyndication.com
User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.6) Gecko/20040113
Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,image/jpeg,image/gif;q=0.2,*/*;q=0.1
Accept-Language: en-us,en;q=0.5
Accept-Encoding: gzip,deflate
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
Keep-Alive: 300
Connection: keep-alive
Referer: http://www.ethereal.com/download.html


	1430
HTTP/1.1 200 OK
P3P: policyref="http://www.googleadservices.com/pagead/p3p.xml", CP="NOI DEV PSA PSD IVA PVD OTP OUR OTR IND OTC"
Content-Type: text/html; charset=ISO-8859-1
Content-Encoding: gzip
Server: CAFE/1.0
Cache-control: private, x-gzip-ok=""
Content-length: 1272
Date: Thu, 13 May 2004 10:17:14 GMT

...........W.s.8..~...mI....y..1y..Mz..7.O7.%.....d.M.....p d.....a...v...{...~/...{JO9..~n4~...6....(.,.Tv.e.Sr.mL.8K..-
..m..Y<hF.3.4%....S...C...A..X.....x*.u.k,...1.y...ZK....t.+U.....mv....3.......2.*.,...Fy..i...d..:.......4..B..t%..L..9..-$B.]...mmU.x1...X.l.(.AL.f.....dX..KAh....Q......p$u.=1..;D...'.!%...Bw..{.Y/T...<...GY9J....?;.ww...Ywf..... >6..Ye.X..H_@.X.YM.$......#:.....D..~O..STrt..,4....H9W..!E.....&.X.=..P9..a...<...-.O.l.-m....h..p7.(O?.a..:..-knhie...
.q.ZU....#....ps..g...p.u.T...`.bp.d.B.r....H...@........L..T.#!Cj.b.l.l....a..........,drp.4..........:aj.....p.H...=......7z...M.........w...y`....In.p...........'.0hnp'..T*.@/.w..@5<..(..{5@_ ../.......}r.........=K....J...qcbX..}.Q.... .>.R....<.......b...sH.u.R...T.>.x.J.+.tb).L...U.(...>.........bOO.....m..OP.o.F'L..
....m..(:m.0.h..A].eBj.......
	160
)...$.P.+-...J.yQ\.v.r..m..j..h...+.%@..yP....o..%
..g.A.x..;.M..6./...{..9....H.W.a.qz...O.....B..
===================================================================
```

### Export Objects

This option is used to extract files from DICOM, HTTP, SMB and TFTP. The query consists of:

- **Main parameter and Protocol**: `--export-objects http`
- **Target folder**: Target folder to save the files

To filter the packets and extract the files within the HTTP protocol you can use a query like `--export-objects http,/path/to/your/folder -q`

!!! tip
    Like with [Streams](#follow-stream), you can switch the HTTP protocol with DICOM, IMF, SMB and TFTP.

```console
user@host:~$ tshark -r demo.pcapng --export-objects http,/home/ubuntu/Desktop/extracted -q
user@host:~$ ls -l /home/ubuntu/Desktop/extracted
total 24
-rw-r--r-- 1 ubuntu ubuntu  3608 Aug 11 18:30 'ads%3fclient=ca-pub-2309191948673629&random=1084443430285&lmt=1082467020&format=468x60_as&output=html&url=http%3A%2F%2Fwww.ethereal.com%2Fdownload.html&color_bg=FFFFFF&color_text=333333&color_link=000000&color_url=666633&color_border=666633'
-rw-r--r-- 1 ubuntu ubuntu 18070 Aug 11 18:30  download.html
```

### Credentials

The *Credentials* option can be used to detect and collect cleartext credentials from FTP, HTTP, IMAP, POP and SMTP. You can filter and find credentials using the parameter like `-z credentials -q`

```console
user@host:~$ tshark -r credentials.pcap -z credentials -q
===================================================================
Packet     Protocol         Username         Info            
------     --------         --------         --------
72         FTP              admin            Username in packet: 37
80         FTP              admin            Username in packet: 47
83         FTP              admin            Username in packet: 54
118        FTP              admin            Username in packet: 93
123        FTP              admin            Username in packet: 97
129        FTP              admin            Username in packet: 101
136        FTP              admin            Username in packet: 106
150        FTP              admin            Username in packet: 115
156        FTP              admin            Username in packet: 120
167        FTP              administrator    Username in packet: 133
207        FTP              administrator    Username in packet: 170
220        FTP              administrator    Username in packet: 184
230        FTP              administrator    Username in packet: 193
250        FTP              administrator    Username in packet: 222
264        FTP              administrator    Username in packet: 235
274        FTP              administrator    Username in packet: 243
286        FTP              administrator    Username in packet: 254
288        FTP              administrator    Username in packet: 258
305        FTP              administrator    Username in packet: 276
312        FTP              administrator    Username in packet: 279
349        FTP              administrator    Username in packet: 314
353        FTP              administrator    Username in packet: 317
370        FTP              administrator    Username in packet: 337
390        FTP              administrator    Username in packet: 362
===================================================================
```

## Advanced Filtering Options

Sometimes, in-depth packet analysis requires special filtering that is not covered by default filters. TShark supports Wireshark's **contains** and **matches** operators, which are the key to advanced filtering options. You can find more about these operators in the [Wireshark Advanced Guide](../wireshark/wireshark_advanced.md#advanced-filtering).

!!! note
    **contains** and **matches** cannot be used with fields consisting of *integer* values.

!!! tip
    Using HEX and regex values instead of ASCII always has a better chance of a match.

### Extract fields

This option is used to extract specific parts of the data from packets. It enables you to collect and correlate various fields from packets. It also helps to manage the query output from the terminal. The query structure requires:

- **Main Filter**: `-T fields`
- **Target Field**: `-e <field name>`
- **Show Field Name**: `-E header=y`

An example query looks for the *IPv4 Source and Destination* looks like `-T fields -e ip.src -e ip.dst -E header=y`.

!!! note
    You need to use the `-e` parameter for each field you want to display.

```console
user@host:~$ tshark -r demo.pcapng -T fields -e ip.src -e ip.dst -E header=y -c 5
ip.src	ip.dst
145.254.160.237	65.208.228.223
65.208.228.223	145.254.160.237
145.254.160.237	65.208.228.223
145.254.160.237	65.208.228.223
65.208.228.223	145.254.160.237
```

### Contains Filter

This filter searches for a value inside packets. It is case-sensitive and provides a similar functionality to the *Find* option by focusing on a specific field.

```console
user@host:~$ tshark -r demo.pcapng -Y 'http.server contains "Apache"'
  38   4.846969 65.208.228.223 ? 145.254.160.237 HTTP/XML 478 HTTP/1.1 200 OK
user@host:~$ tshark -r demo.pcapng -Y 'http.server contains "Apache"' -T fields -e ip.src -e ip.dst -e http.server -E header=y
ip.src	ip.dst	http.server
65.208.228.223	145.254.160.237	Apache
```

### Matches Filter

This filter searches for a pattern of a regular expression. It is also case-sensitive and complex queries have a margin of error.

```console
user@host:~$ tshark -r demo.pcapng -Y 'http.request.method matches "(GET|POST)"'
    4   0.911310 145.254.160.237 ? 65.208.228.223 HTTP 533 GET /download.html HTTP/1.1 
   18   2.984291 145.254.160.237 ? 216.239.59.99 HTTP 775 GET /pagead/ads?client=ca-pub-2309191948673629&random=1084443430285&lmt=1082467020&format=468x60_as&output=html&url=http%3A%2F%2Fwww.ethereal.com%2Fdownload.html&color_bg=FFFFFF&color_text=333333&color_link=000000&color_url=666633&color_border=666633 HTTP/1.1
user@host:~$ tshark -r demo.pcapng -Y 'http.request.method matches "(GET|POST)"' -T fields -e ip.src -e ip.dst -e http.request.method -E header=y
ip.src	ip.dst	http.request.method
145.254.160.237	65.208.228.223	GET
145.254.160.237	216.239.59.99	GET
```

## Extracting data

While investigating it is important to know how to extract hostnames, DNS queries and user agents. 

### Extract Hostnames

The option to extract hostnames is `-e dhcp.option.hostname`

```console
user@host:~$ tshark -r hostnames.pcapng -T fields -e dhcp.option.hostname
92-rkd
92-rkd
T3400

T3400

60-alfb-sec2
60-alfb-sec2


aminott
aminott
90-tasd-sec

90-tasd-sec

...
```

This is the output delivered by DHCP packets. It isn't easy to manage when multiple duplicate values exists. Using a few Linux tools and utilities helps you to manage and organize the command line output.

```console
user@host:~$ tshark -r hostnames.pcapng -T fields -e dhcp.option.hostname  | awk NF | sort -r | uniq -c | sort -r
     26 202-ac
     18 92-rkd
     14 93-sts-sec
     12 prus-pc
     10 90-tasd-sec
     10 60-alfb-sec2
      8 12-wew-sec
      6 temp_open
      6 off-admin-ass
      6 aminott
      ...
```

!!! note
    You can find more about these Linux utilities [here](../../../servers/linux/commands.md)

### Extract DNS Queries

```console
user@host:~$ tshark -r dns-queries.pcap -T fields -e dns.qry.name | awk NF | sort -r | uniq -c | sort -r
    472 db.rhodes.edu
     96 connectivity-check.ubuntu.com.rhodes.edu
     94 connectivity-check.ubuntu.com
      8 3.57.20.10.in-addr.arpa
      4 e.9.d.b.c.9.d.7.1.b.0.f.a.2.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.8.e.f.ip6.arpa
      4 6.7.f.8.5.4.e.f.f.f.0.d.4.d.8.8.0.0.0.0.0.0.0.0.0.0.0.0.0.8.e.f.ip6.arpa
      4 3.4.b.1.3.c.e.f.f.f.4.0.e.e.8.7.0.0.0.0.0.0.0.0.0.0.0.0.0.8.e.f.ip6.arpa
      4 1.1.a.2.6.2.e.f.f.f.1.9.9.f.8.6.0.0.0.0.0.0.0.0.0.0.0.0.0.8.e.f.ip6.arpa
      4 1.0.18.172.in-addr.arpa
      4 1.0.17.172.in-addr.arpa
      4 0.f.2.5.6.b.e.f.f.f.b.7.2.4.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.e.f.ip6.arpa
      2 _ipps._tcp.local,_ipp._tcp.local
      2 84.170.224.35.in-addr.arpa
      2 22.2.10.10.in-addr.arpa
      2 21.2.10.10.in-addr.arpa
```

### Extract User Agents

```console
user@host:~$ tshark -r user-agents.pcap -T fields -e http.user_agent | awk NF | sort -r | uniq -c | sort -r
      9 Wfuzz/2.4
      6 Mozilla/5.0 (Windows; U; Windows NT 6.4; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.237 Safari/534.10
      5 Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0
      5 Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.32 Safari/537.36
      4 sqlmap/1.4#stable (http://sqlmap.org)
      3 Wfuzz/2.7
      3 Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)
      2 Microsoft-WNS/10.0
      1 Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36
```




