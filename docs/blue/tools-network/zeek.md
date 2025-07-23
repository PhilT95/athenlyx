# Zeek - Traffic Analyser
>Zeek (formerly Bro) is the world's leading platform for network security monitoring. Flexible, open-source, and powered by defenders." "Zeek is a passive, open-source network traffic analyser. Many operators use Zeek as a network security monitor (NSM) to support suspicious or malicious activity investigations. Zeek also supports a wide range of traffic analysis tasks beyond the security domain, including performance measurement and troubleshooting.

## Zeek Basics
**Zeek** differs from known monitoring and IDS/IPS (like [Snort](./snort.md)) tools by providing a wide range of detailed logs ready to investigate both forensic and data analysis actions.

Compared to <ins>Snort</ins>, Zeek is harder to use, but offers in-depth traffic visibility and is more useful for threat hunting. It can detect complex threats and has a scripting language. It supports event correlation and the logs are easier to read. 

### Zeek Architecture

Zeek has to primary layers:

1. **Event Engine**: This layer is where the packets are proccessed. It is called the event core and is responsible for describing the event without focusing on the event details. It devides the packatges into parts souch as
   - Source & Destination address
   - protocol identification
   - session analysis
   - file extraction
2. **Policy Script Interpreter**: This layer conducts the semantic analysis . It is responsible for describing the event correlations by using **Zeek Scripts**.

### Zeek Frameworks
Zeek has several frameworks to provide extended functionality in the scripting layer. These frameworks enhance Zeek's flexibility and compatibility with other network components. Each framework focuses on the specific use case and easily runs with Zeek installation.

**Available Frameworks**

|Logging|Notice|Input|Configuration|Intelligence|
|:------|:-----|:----|:------------|:-----------|
|Cluster|Broker Communication|Supervisor|GeoLocation|File Analysis|
|Signature|Summary|NetControl|Packet Analysis|TLS Decryption|

You can find more about frameworks [here](https://docs.zeek.org/en/master/frameworks/index.html)


### Basic Commands
Once you start Zeek, it will automatically start investigation the traffic or any given pcap file and generate logs. If you process a pcap file, the logs will be generated in the working directory. If Zeek runs as a service, the default directory is ``/opt/zeek/logs`` 

Zeek always needs to be started with superuser permissions!

You can run `zeekctl` to get the following output and puts you into the **ZeekControl** console

```bash
Warning: new zeek version detected (run the zeekctl "deploy" command)

Welcome to ZeekControl 2.4.0

Type "help" for help.

[ZeekControl] >
```

You can run commands like **status**,**start** and **stop** within this console

```bash
[ZeekControl] > status
Name         Type       Host          Status    Pid    Started
zeek         standalone localhost     stopped
[ZeekControl] > start
starting zeek ...
[ZeekControl] > status
Name         Type       Host          Status    Pid    Started
zeek         standalone localhost     running   8100   21 Jul 17:31:06
[ZeekControl] > stop
stopping zeek ...
[ZeekControl] > status
Name         Type       Host          Status    Pid    Started
zeek         standalone localhost     stopped
```

You can also run these commands using 

- `zeekctl status`
- `zeekctl start`
- `zeekctl stop`

If you want to listen to live traffic, Zeek needs to be started as a service. To run Zeek as a packet investigator for processing pcaps for example, you need to execute the following command:
`zeek -C -r sample.pcap`

The main command line parameters are the following

|Parameter|Description|
|:--------|:----------|
|`-r`|Reading option, read/process a pcap file|
|`-C`|Ingnoring checksum erros|
|`-v`|Version information|
|`zeekctl`|Starts the ZeekControl module|

## Zeek Logging
Zeek generates a lot of log files since they are created according to traffic data. There will be a log for every connection in the wire, including the application level protocols and fields.

In a nutshell, Zeek has the following log files:

|Category|Description|Log Files|
|:-------|:----------|:--------|
|Network|Network protocol logs|conn.log, dce_rpc.log, dhcp.log, dnp3.log, dns.log, ftp.log, http.log, irc.log, kerberos.log, modbus.log, modbus_register_change.log, mysql.log, ntlm.log, ntp.log, radius.log, rdp.log, rfb.log, sip.log, smb_cmd.log, smb_files.log, smb_mapping.log, smtp.log, snmp.log, socks.log, ssh.log, ssl.log, syslog.log, tunnel.log.|
|Files|File analysis result logs| files.log, ocsp.log, pe.log, x509.log.|
|NetControl|Network control and flow logs|netcontrol.log, netcontrol_drop.log, netcontrol_shunt.log, netcontrol_catch_release.log, openflow.log.|
|Detection|Detection and possible indicator logs.|netcontrol.log, netcontrol_drop.log, netcontrol_shunt.log, netcontrol_catch_release.log, openflow.log.|
|Network Observations|Network flow logs.|netcontrol.log, netcontrol_drop.log, netcontrol_shunt.log, netcontrol_catch_release.log, openflow.log.|
|Miscellaneous|Additional logs cover external alerts, inputs and failures.|barnyard2.log, dpd.log, unified2.log, unknown_protocols.log, weird.log, weird_stats.log.|
|Zeek Diagnostics| Zeek diagnostic logs cover system messages, actions and some statistics.| broker.log, capture_loss.log, cluster.log, config.log, loaded_scripts.log, packet_filter.log, print.log, prof.log, reporter.log, stats.log, stderr.log, stdout.log.|

Those are a lot of logs, but the most commonly used logs are these:

|Overall Info|Protocol Based|Detection|Observations|
|:-----------|:-------------|:--------|:-----------|
|conn.log|http.log|notice.log|known_hosts.log|
|files.log|dns.log|singatures.log|known_services.log|
|intel.log|ftp.log|pe.log|software.log|
|loaded_scripts.log|ssh.log|traceroute.log|weird.log|

To read the log files, a program called **zeek-cut** can be used to reduce the effort of extracting specific columns from log files.
This works by using **cat** to read the information and piping it into **zeek-cut**, which can extract only the important fields.

```bash
root@machine$ cat conn.log
#fields	ts	uid	id.orig_h	id.orig_p	id.resp_h	id.resp_p	proto	service	duration	orig_bytes	resp_bytes	conn_state	local_orig	local_resp	missed_bytes	history	orig_pkts	orig_ip_bytes	resp_pkts	resp_ip_bytes	tunnel_parents
#types	time	string	addr	port	addr	port	enum	string	intervalcount	count	string	bool	bool	count	string	count	count	count	count	set[string]
1488571051.943250	ClYr422WGihaDJ8rnf	192.168.121.2	51153	192.168.120.22	53	udp	dns	0.001263	36	106	SF	-	-0	Dd	1	64	1	134	-
1488571038.380901	C290JU161urwnXw0s7	192.168.121.10	50080	192.168.120.10	514	udp	-	0.000505	234	0	S0	-	-0	D	2	290	0	0	-
...

root@machine$ cat conn.log | zeek-cut proto id.orig_h id.orig_p id.resp_h id.resp_p
udp	192.168.121.2	51153	192.168.120.22	53
udp	192.168.121.10	50080	192.168.120.10	514
udp	192.168.121.40	123	    212.224.120.164	123
udp	192.168.121.40	123	    78.46.107.140	123
udp	192.168.121.2	64199	192.168.121.254	1967
udp	192.168.121.2	64091	192.168.121.253	1967
udp	192.168.121.2	64091	192.168.121.253	65534
udp	192.168.121.2	64199	192.168.121.254	65535

```

You can add and remove fields as you like or need. Bases on the output you can use another pipe to sort and further filter your data by using
```bash
root@machine$ cat conn.log | zeek-cut proto duration | sort
```

## Zeek Signatures
Zeek supports signatures to have rules and event correlations to find noteworthy activities on the network. Zeek signatures use low-level pattern matching and cover conditions similar to Snort rules. Unlike Snort rules, Zeek rules are not the primary event detection point. Zeek has a scripting language and can chain multiple events to find an event of interest. We focus on the signatures in this task, and then we will focus on Zeek scripting in the following tasks.

Zeek signatures consist of three logical paths:

- **Signature ID**: unique signature name
- **Conditions**: Filtering the packet headers or the content for source/destination addresses, protocols, port numbers or a specific value/pattern
- **Action**
  - *Default action*: Create the signatures.log file in case of a signature match
  - *Additional action*: Trigger a zeek script

You can run zeek with a signature file this way:
```bash
root@machine$ zeek -C -r sample.pcap -s sample.sig
```


### Signature Example 01 - HTTP Cleartext Passwords
```bash
signature http-password {
     ip-proto == tcp
     dst-port == 80
     payload /.*password.*/
     event "Cleartext Password Found!"
}

# signature: Signature name.
# ip-proto: Filtering TCP connection.
# dst-port: Filtering destination port 80.
# payload: Filtering the "password" phrase.
# event: Signature match message.
```
### Signature Example 02 - FTP Admin Login attempts

```bash
signature ftp-admin {
     ip-proto == tcp
     ftp /.*USER.*dmin.*/
     event "FTP Admin Login Attempt!"
}
```
### Signature Example 03 - FTP Brute Force attempts

This signature looks for the FTP response code **530**

```bash
signature ftp-brute {
     ip-proto == tcp
     payload /.*530.*Login.*incorrect.*/
     event "FTP Brute-force Attempt"
}
```
### Signature Example 05 - Multiple signatures
This signature looks for the FTP response code **530**

```bash
signature ftp-username {
    ip-proto == tcp
    ftp /.*USER.*/
    event "FTP Username Input Found!"
}

signature ftp-brute {
     ip-proto == tcp
     payload /.*530.*Login.*incorrect.*/
     event "FTP Brute-force Attempt"
}
```

## Zeek Scripts
Zeek has its own event-driven scripting language, which is as powerful as high-level languages and allows us to investigate and correlate the detected events.

- **Zeek base scripts** are installed by default and not intended to be modified. They are located in `/opt/zeek/share/zeek/base`
- **User generated or modified scripts** should be located in a specific path `/opt/zeek/share/zeek/site`
- **Policy scripts** are located in `/opt/zeek/share/zeek/policy`
- To use a script in sniffing mode, you must identify the script in the Zeek configuration file. You can also use a script for a single run, just like signatures. The configuration file is located in `/opt/zeek/share/zeek/site/local.zeek`

A simple zeek script to extract DHCP hostnames can look like this:

```bash
event dhcp_message (c: connection, is_orig: bool, msg: DHCP::Msg, options: DHCP::Options)
{
print options$host_name;
}
```