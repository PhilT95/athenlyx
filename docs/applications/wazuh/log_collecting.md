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

