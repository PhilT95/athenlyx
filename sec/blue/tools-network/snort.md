# Snort - Intrusion Prevention System (IPS)
>Snort is the foremost Open Source Intrusion Prevention System (IPS) in the world. Snort IPS uses a series of rules that help define malicious network activity and uses those rules to find packets that match against them and generates alerts for users.
>
> Snort can be deployed inline to stop these packets, as well. Snort has three primary uses: As a packet sniffer like tcpdump, as a packet logger — which is useful for network traffic debugging, or it can be used as a full-blown network intrusion prevention system. Snort can be downloaded and configured for personal and business use alike.  

<p align="right"><a herf="https://www.snort.org/">snort.org</a></p>
 

## Basic commands

All commands are options for launching the **snort** binary.

|Command|Function|Example|
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
|`-A console`| This will start snort as an IDP/IPS with a **fast style alert console (-A console)**|`sudo snort -c snort.conf -A console`|
|`-A cmg`| This will start snort as an IDP/IPS with a **basic header details via in hex and text format (-A cmg)**|`sudo snort -c snort.conf -A cmg`|
|`-A fast`| This will start snort as an IDP/IPS with a fast mode that provides **alerts, messages, timestamps and source/destination ip addresses (-A fast)**. No console output will be shown. Instead a alert file will be created. The alert file can be created by appending `-l .` to the command.|`sudo snort -c snort.conf -A fast`|
|`-A full`| This will start snort as an IDP/IPS with a full mode that provides **all information (-A full)**. Instead a alert file will be created. The alert file can be created by appending `-l .` to the command.|`sudo snort -c snort.conf -A full`|
|`-A none`| This will start snort as an IDP/IPS with a none mode that **doesn't create an alert file. (-A full)**|`sudo snort -c snort.conf -A none`|
|`-Q --daq afpacket` `-i`| This will start snort with an activated **Data Aquisition (DAQ)** module and use the **afpacket** module to use snort as an IPS on the given intertface **eth0:eth1**|`sudo snort -c /etc/snort/snort.conf -q -Q --daq afpacket -i eth0:eth1 -A console`|