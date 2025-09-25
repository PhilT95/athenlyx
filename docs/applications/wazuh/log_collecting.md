# Collecting Logs with Wazuh

## Collecting Windows Logs with Wazuh

All sorts of actions and events are captured on a Windows OS. This includes authentication attempts, networking connections and many more. This information is stored in the [Windows Event Logs](../../blue/endpoint-security/windows/windows_event_logs.md) using the [Sysmon](../../blue/endpoint-security/windows/sysmon.md) tool.

Wazuh can be used to aggregate these events recorded by *Sysmon* for processing to the Wazuh manager. This requires configuration changes to both the Wazuh agent and the Sysmon application. 

??? example "Sysmon configuration file for monitoring PowerShell processes"
    
    ```xml
    Sysmon schemaversion="3.30" 
        HashAlgorithms md5 /HashAlgorithms 
    EventFiltering 
    !--SYSMON EVENT ID 1 : PROCESS CREATION-- 
    ProcessCreate onmatch="include" 
    Image condition="contains" powershell.exe /Image 
    /ProcessCreate 
    !--SYSMON EVENT ID 2 : FILE CREATION TIME RETROACTIVELY CHANGED IN THE FILESYSTEM-- 
    FileCreateTime onmatch="include"  /FileCreateTime 
    !--SYSMON EVENT ID 3 : NETWORK CONNECTION INITIATED-- 
    NetworkConnect onmatch="include"  /NetworkConnect 
    !--SYSMON EVENT ID 4 : RESERVED FOR SYSMON STATUS MESSAGES, THIS LINE IS INCLUDED FOR DOCUMENTATION PURPOSES ONLY-- 
    !--SYSMON EVENT ID 5 : PROCESS ENDED-- 
    ProcessTerminate onmatch="include"  /ProcessTerminate 
    !--SYSMON EVENT ID 6 : DRIVER LOADED INTO KERNEL-- 
    DriverLoad onmatch="include"  /DriverLoad  
    !--SYSMON EVENT ID 7 : DLL (IMAGE) LOADED BY PROCESS-- 
    ImageLoad onmatch="include"  /ImageLoad 
    !--SYSMON EVENT ID 8 : REMOTE THREAD CREATED-- 
    CreateRemoteThread onmatch="include"  /CreateRemoteThread 
    !--SYSMON EVENT ID 9 : RAW DISK ACCESS-- 
    RawAccessRead onmatch="include"  /RawAccessRead  
    !--SYSMON EVENT ID 10 : INTER-PROCESS ACCESS-- 
    ProcessAccess onmatch="include"  /ProcessAccess 
    !--SYSMON EVENT ID 11 : FILE CREATED-- 
    FileCreate onmatch="include"  /FileCreate 
    !--SYSMON EVENT ID 12 & 13 & 14 : REGISTRY MODIFICATION-- 
    RegistryEvent onmatch="include"  /RegistryEvent 
    !--SYSMON EVENT ID 15 : ALTERNATE DATA STREAM CREATED-- 
    FileCreateStreamHash onmatch="include"  /FileCreateStreamHash  
    PipeEvent onmatch="include"  /PipeEvent 
    /EventFiltering 
    /Sysmon 
    ```

To instruct Sysmon to log events, the Sysmon application needs to be executed while providing the configuration file.

!!! tip
    The configuration file can be provided as a parameter like this:  
    ``Sysmon64.exe -accepteula -i configuration.xml``

Once Sysmon starts logging the configuration files, the Wazuh agent needs to be instructed to send these events to the Wazu management server. This can be done by adjusting the Wazu agent configuration file located at ``C:\Program Files (x86)\ossec-agent\ossec.conf``

```xml
<!--
  Wazuh - Agent - Default configuration for Windows
  More info at: https://documentation.wazuh.com
  Mailing list: https://groups.google.com/forum/#!forum/wazuh
-->

<ossec_config>

  <client>
    <server>
      <address>wazuh.server</address>
      <port>1514</port>
      <protocol>tcp</protocol>
    </server>
    <config-profile>windows, windows10</config-profile>
    <crypto_method>aes</crypto_method>
    <notify_time>10</notify_time>
    <time-reconnect>60</time-reconnect>
    <auto_restart>yes</auto_restart>
    <enrollment>
      <enabled>yes</enabled>
      <agent_name>Agent_Name</agent_name>
      <groups>default</groups>
    </enrollment>
  </client>


  <!-- Agent buffer options -->
  <client_buffer>
    <disabled>no</disabled>
    <queue_size>5000</queue_size>
    <events_per_second>500</events_per_second>
  </client_buffer>

  <!-- Log analysis -->
  <localfile>
    <location>Application</location>
    <log_format>eventchannel</log_format>
  </localfile>

  <localfile>
    <location>Security</location>
    <log_format>eventchannel</log_format>
    <query>Event/System[EventID != 5145 and EventID != 5156 and EventID != 5447 and
      EventID != 4656 and EventID != 4658 and EventID != 4663 and EventID != 4660 and
      EventID != 4670 and EventID != 4690 and EventID != 4703 and EventID != 4907 and
      EventID != 5152 and EventID != 5157]</query>
  </localfile>
  ...
```

To include the Sysmon Log, the following snippet needs to be added:

```xml
<!-- Sysmon Analysis -->
<localfile>
    <location>Microsoft-Windows-Sysmon/Operational</location>
    <log_format>eventchannel</log_format>
</localfile>
```

This can be added below the already existing ``localfile`` snippets. After this, the agent needs to be restarted. The last thing to do is telling the Wazuh management server to add Sysmon as a rule to visualize these events. This can be done by adding an XML snippet to the local rules located in ``/var/ossec/etc/rules/local_rules.xml``

```xml
<group name="sysmon,">
 <rule id="255000" level="12">
    <if_group>sysmon_event1</if_group>
    <field name="sysmon.image">\\powershell.exe||\\.ps1||\\.ps2</field>
    <description>Sysmon - Event 1: Bad exe: $(sysmon.image)</description>
    <group>sysmon_event1,powershell_execution,</group>
 </rule>
</group>
```

## Collecting Linux Logs

Capturing logs from a Linux agent is a more simple process similar to capturing events from a Windows agent. Wazuh already has many *out of the box* rules to analyze log files which can be found here ``/var/ossec/ruleset/rules`` on the Wazuh server.

```console
[user@wazuh user]# ls /var/ossec/ruleset/rules/
0010-rules_config.xml       0110-ms_dhcp_rules.xml           0215-policy_rules.xml      0320-clam_av_rules.xml           0420-freeipa_rules.xml                 0530-mysql_audit_rules.xml         0625-cisco-asa_rules.xml          0830-sysmon_id_11.xml
0015-ossec_rules.xml        0115-arpwatch_rules.xml          0220-msauth_rules.xml      0325-opensmtpd_rules.xml         0425-cisco-estreamer_rules.xml         0535-mariadb_rules.xml             0625-mcafee_epo_rules.xml         0840-win_event_channel.xml
0016-wazuh_rules.xml        0120-symantec-av_rules.xml       0225-mcafee_av_rules.xml   0330-sysmon_rules.xml            0430-ms_wdefender_rules.xml            0540-pfsense_rules.xml             0630-nextcloud_rules.xml          0850-audit_rules.xml
0017-wazuh-api_rules.xml    0125-symantec-ws_rules.xml       0230-ms-se_rules.xml       0335-unbound_rules.xml           0435-ms_logs_rules.xml                 0545-osquery_rules.xml             0635-owlh-zeek_rules.xml          0860-sysmon_id_13.xml
0020-syslog_rules.xml       0130-trend-osce_rules.xml        0235-vmware_rules.xml      0340-puppet_rules.xml            0440-ms_sqlserver_rules.xml            0550-kaspersky_rules.xml           0640-junos_rules.xml              0870-sysmon_id_8.xml
0025-sendmail_rules.xml     0135-hordeimp_rules.xml          0240-ids_rules.xml         0345-netscaler_rules.xml         0445-identity_guard_rules.xml          0555-azure_rules.xml               0675-panda-paps_rules.xml         0900-firewall_rules.xml
0030-postfix_rules.xml      0140-roundcube_rules.xml         0245-web_rules.xml         0350-amazon_rules.xml            0450-mongodb_rules.xml                 0560-docker_integration_rules.xml  0680-checkpoint-smart1_rules.xml  0905-cisco-ftd_rules.xml
0035-spamd_rules.xml        0145-wordpress_rules.xml         0250-apache_rules.xml      0360-serv-u_rules.xml            0455-docker_rules.xml                  0565-ms_ipsec_rules.xml            0690-gcp_rules.xml                0910-ms-exchange-proxylogon_rules.xml
0040-imapd_rules.xml        0150-cimserver_rules.xml         0255-zeus_rules.xml        0365-auditd_rules.xml            0460-jenkins_rules.xml                 0570-sca_rules.xml                 0695-f5_bigip_rules.xml           0915-win-powershell_rules.xml
...
```

Not all of these rules are enabled but can be by editing the Wazuh agent configuration that is sending logs to the Wazuh management server with the configuration file ``/var/ossec/etc/ossec.conf``.


!!! example "Adding nginx monitoring to the agent ruleset"
    To let the Wazuh agent monitor the nginx logs, the following snippet needs to be added to the configuration file:

    ```xml
    <!-- nginx Log Analysis -->
    <localfile>
      <location>/var/log/nginx/website.com\:443.access.log</location>
      <log_format>syslog</log_format>
    </localfile>
    ```

    Please adjust the config to the configuration file(s) you want to monitor.

### Auditing Commands

Wazuh used the ``auditd`` package that can be installed on Debian/Ubuntu, RedHat and its derivates. ``auditd`` monitors the system for certain actions and events and will write this to a log file. The log collector then can be used to read this log file and send it to the Wazuh management server for processing. On AlmaLinux (a RedHat derivate) for example, this package is installed by default. If not, the installation is rather simple.


=== "Ubuntu"

    ```console
    $ sudo apt-get install auditd audispd-plugins
    $ sudo systemctl enable auditd.service
    $ sudo systemctl start auditd.service
    ```

=== "Almalinux"

    ```console
    [user@server ~] sudo dnf -y install auditd
    [user@server ~] sudo systemctl enable --now auditd
    ```

=== "Debian"

  ```console
  user@server:~# sudo apt -y install auditd
  ```

``Auditd`` can also be used to monitor custom commands and events. For example, it can be extended to monitor for commands like ``tcpdump``, ``netcat`` or ``cat`` for files such as ``/etc/passwd`` which are signs of a breach. The rules for ``Auditd`` can be found in the directory ```/etc/auditd/rules.d/audit.rules``. 

!!! example "Monitoring commands executed as root"

    To monitor commands executed as root, ``-a exit,always -F arch=b64 -F euid=0 -S execve -k audit-wazuh-c`` needs to be added to the ``audit.rules`` file.

    ```    
    ## First rule - delete all
    -D

    ## Increase the buffers to survive stress events.
    ## Make this bigger for busy systems
    -b 8192

    ## This determine how long to wait in burst of events
    --backlog_wait_time 60000

    ## Set failure mode to syslog
    -f 1

    -a exit,always -F arch=b64 -F euid=0 -S execve -k audit-wazuh-c
    ```

    ``Auditd`` needs to be informed of this new rule. This can be done using the following command:

    ```console
    [user@server]# sudo auditctl -R /etc/audit/rules.d/audit.rules
    ```

    Verify that the Wazuh agent is already monitoring the log file located under ``/var/log/audit/audit.log``. The following snippet needs to exist inside the configuration.

    ```xml    
    <localfile>
      <log_format>audit</log_format>
      <location>/var/log/audit/audit.log</location>
    </localfile>
    ```




