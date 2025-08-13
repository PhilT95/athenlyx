# Snort - Intrusion Prevention System (IPS)
>Snort is the foremost Open Source IPS in the world. Snort IPS uses a series of rules that help define malicious network activity and uses those rules to find packets that match against them and generates alerts for users.
>
> Snort can be deployed inline to stop these packets, as well. Snort has three primary uses: As a packet sniffer like tcpdump, as a packet logger — which is useful for network traffic debugging, or it can be used as a full-blown network IPS. Snort can be downloaded and configured for personal and business use alike.  

<p align="right"><a herf="https://www.snort.org/">snort.org</a></p>
 

## Basic commands

All commands are options for launching the **snort** binary.

|Parameter|Function|Example|
|:-------| :------|---------|
|`V`| Shows the version of instance|`snort -V`|
|`-c` `-d`|**-T** is used to test the provided configuration and **-c** is used to identify the configuration|`sudo snort -c ./snort.conf -T`|`sudo snort -c ./snort.conf -T`|
|`-v`| This will start snort in the **verbode mode (-v)**|`sudo snort -v`|
|`-d`| This will start snort in the **dumping packet data mode (-d)**|`sudo snort -d`|
|`-de`| This will start snort in the **dump (-d)** and **link-layer header grabbing (-e)** mode|`sudo snort -de`|
|`-X`| This will start snort in **full packet dump mode (-X)**|`sudo snort -X`|
|`dev` `-l`| This will start snort with the **-d, -e** and **-v** modes and enabled **logging (-l)** to the provided directory. In this case it will be the directory you are currently in **(.)**| `sudo snort -dev -l .`|
|`-K ASCII`| This will write the log in **ASCII-format (-K ASCII)**|`sudo snort -dev -K ASCII -l .`|
|`-r`| This will start snort in the **packet reader mode (-r)**|`sudo snort -r snort.log`|
|`-r`| This will read and search the log for all entries with port 53/udp.You can also provide *udp*, *ICMP* or *tcp* as commands without a port and it will search and display relevant logs.|`sudo snort -r logname.log 'udp and port 53`|
|`-dvr`| This will display only the first 10 entries of the log file|`sudo snort -dvr logname.log -n 10`|
|`-c` `-N`| This will start snort as an IDP/IPS without logging and the provided configuration|`sudo snort -c snort.conf -N`|
|`-D`| This will start snort as an IDP/IPS in the background and the provided configuration|`sudo snort -c snort.conf -D`|
|`-A console`| This will start snort as an IDP/IPS with a **fast style alert console (-A console)**. This prevents packages from being dropped.|`sudo snort -c snort.conf -A console`|
|`-A cmg`| This will start snort as an IDP/IPS with a **basic header details via in hex and text format (-A cmg)**|`sudo snort -c snort.conf -A cmg`|
|`-A fast`| This will start snort as an IDP/IPS with a fast mode that provides **alerts, messages, timestamps and source/destination ip addresses (-A fast)**. No console output will be shown. Instead a alert file will be created. The alert file can be created by appending `-l .` to the command.|`sudo snort -c snort.conf -A fast`|
|`-A full`| This will start snort as an IDP/IPS with a full mode that provides **all information (-A full)**. Instead a alert file will be created. The alert file can be created by appending `-l .` to the command.|`sudo snort -c snort.conf -A full`|
|`-A none`| This will start snort as an IDP/IPS with a none mode that **doesn't create an alert file. (-A full)**|`sudo snort -c snort.conf -A none`|
|`-Q --daq afpacket` `-i`| This will start snort with an activated **Data Aquisition (DAQ)** module and use the **afpacket** module to use snort as an IPS on the given interface **eth0:eth1**. The DAQ is needed for enabling snort to drop packages.|`sudo snort -c /etc/snort/snort.conf -q -Q --daq afpacket -i eth0:eth1 -A console`|


## How to read PCAPs with snort

|Parameter|Function|Example|
|:-------| :------|---------|
|`-r filehere`|Reads a single pcap|`sudo snort -r icmp-test.pcap`|
|`--pcap-list=""`|Reads pcaps provided in command (space separated)|`sudo snort -r --pcap-list=="icmp-test.pcap http2.pcap" `|
|`--pcap-show`|Shows pcap name on console during processing|`sudo snort -c /etc/snort/snort.conf -q --pcap-list="icmp-test.pcap http2.pcap" -A console --pcap-show `|


!!! tip "Command to get full result overview"
  A handy command to get a full overview over the results is `sudo snort -c /etc/snort/snort.conf -A full -l . -r file.pcap`  
  You can the number of created alerts, detected TCP packages and much more.


## Understanding Snort Rules
Snort rules consist of the following parameters:

- **Type of Action**: Defines how the snort reacts if the conditions of the rule are met. Types of actions are
    - alert: Generate an alert an log the packet
    - log: Log the packet
    - drop: Block and log the packet
    - reject: Block the packet, log it and terminate the packet session
- **Protocol**: Protocol parameter identifies the type of the protocol that is filtered by the rule. This can be used in combination with ports. Snort supports only:
    - IP
    - TCP
    - UDP
    - ICMP
- **Source and Destination IP**
- **Source and Destination Port**
- **Direction**: This operator indicates the traffic flow filtered by Snort. The left side shows the source and the right side shows the destination.
    - -> means Source to destination
    - <> means bidirectional flow
-  **Options**: There are 3 main rule options in snort:
   -  *General Rule Options*: Fundamental rule options for snort
   -  *Payload Rule Options*: Rule options that help to investigate the payload data
   -  *Non-Payload Rule Options*: Rule options that focus on non-payload data. This option can be used to create specific patterns to identify network issues.


### Fudemental rule options
- **Msg**: The message field is a basic prompt and quick identifier of the rule. Once the rule is triggered, the message filed will appear in the console or log. Usually, the message part is a one-liner that summarizes the event.
- **Sid**: Snort rule IDs (SID) come with a pre-defined scope, and each rule must have a SID in a proper format. There are three different scopes for SIDs shown below:
  - **<100**: Reserved rules
  - **100-999,999**: Rules came with the build.
  - **>=1,000,000**: Rules created by user.
- **Reference**: Each rule can have additional information or reference to explain the purpose of the rule or threat pattern. That could be a Common Vulnerabilities and Exposures (CVE) id or external information. Having references for the rules will always help analysts during the alert and incident investigation.
- **Rev**: Snort rules can be modified and updated for performance and efficiency issues. Rev option help analysts to have the revision information of each rule. Therefore, it will be easy to understand rule improvements. Each rule has its unique rev number, and there is no auto-backup feature on the rule history. Analysts should keep the rule history themselves. Rev option is only an indicator of how many times the rule had revisions.

### Payload Detection Rule options
- **Content**: 	Payload data. It matches specific payload data by ASCII, HEX or both. It is possible to use this option multiple times in a single rule. However, the more you create specific pattern match features, the more it takes time to investigate a packet. Following rules will create an alert for each HTTP packet containing the keyword "GET". This rule option is case sensitive!
  - ASCII mode - `alert tcp any any <> any 80  (msg: "GET Request Found"; content:"GET"; sid: 1000001; rev:1;)`
  - HEX mode - `alert tcp any any <> any 80  (msg: "GET Request Found"; content:"|47 45 54|"; sid: 1000001; rev:1;)`
- **Nocase**: Disabling case sensitivity. Used for enhancing the content searches. \
`alert tcp any any <> any 80  (msg: "GET Request Found"; content:"GET"; nocase; sid: 1000001; rev:1;)`
- **Fast_pattern**: Prioritize content search to speed up the payload search operation. By default, Snort uses the biggest content and evaluates it against the rules. "fast_pattern" option helps you select the initial packet match with the specific value for further investigation. This option always works case insensitive and can be used once per rule. Note that this option is required when using multiple "content" options. \
The following rule has two content options, and the fast_pattern option tells to snort to use the first content option (in this case, "GET") for the initial packet match.\
`alert tcp any any <> any 80  (msg: "GET Request Found"; content:"GET"; fast_pattern; content:"www";  sid:1000001; rev:1;)`

### Non-Payload Detection Rule options

- **ID**: Filtering the IP id field.\
`alert tcp any any <> any any (msg: "ID TEST"; id:123456; sid: 1000001; rev:1;)`
- **Flags**:  Filtering the TCP flags: 
  - F - FIN
  - S - SYN
  - R - RST
  - P - PSH
  - A - ACK
  - U - URG 
  - `alert tcp any any <> any any (msg: "FLAG TEST"; flags:SA;  sid: 100001; rev:1;)`
- **Dsize**: Filtering the packet payload size.
  - dsize:min<>max;
  - dsize:>100
  - dsize:<100
- **Sameip**: Filtering the source and destination IP addresses for duplication.

For a convenient Cheat sheet, see [this one from Tryhackme.com](Snort_Cheatsheet_TryHackMe.pdf)

#### Rule Examples
|Rule|Explanation|
|:----|----------|
|`alert tcp any 21 <> any any (msg:"FTP No Password entered";content:"331";content:"Administrator";sid:1000001;rev:1;)`|This rule will generate an alert for any 21/tcp packages with the return code **331** and **Administrator** inside the content. Regarding the FTP Service this means that there are login attempts by the user **Administrator** without a provided password. See [FTP Return Codes](https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes)
|`alert tcp any any <> any any  (msg: "PNG File Found";content:"\|89 50 4E 47 0D 07 0D 0A 1A 0A\|"; sid: 100001;rev:1;)`|This rule will generate an alert for all packages with the given content. The given content resembles the Hex file signature for .PNG-files. See [Hex File Signatures](https://en.wikipedia.org/wiki/List_of_file_signatures)


The tool **Strings** can help you figure out, which information are hidden inside the generate log. It can be used like this `sudo strings snort.log | grep GIF`.
You can inspect the hex values of a log with `sudo snort snort.log -X`.

!!! tip "Tips and tricks"
  - It is very important to analyze the log files with different options or tools to get all the important    information out of it.
  - Don't forget to look at the alert files as wel