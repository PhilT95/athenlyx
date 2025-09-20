![Wazu Banner](images/wazuh_banner.jpg)

# Wazuh - EDR Software Solution

**Wazuh**, created in 2015, is an open-source, freely available and extensive EDR solution. It can be used in all scales of environments. Wazuh operators on a management and agent module. To put it simply, a device is dedicated to running Wazuh called the *manager*. The *agents* are installed on the devices that need to be monitored. 

If you want to install Wazuh and how to configure it have a look at this [Setup Guide](wazuh_setup.md).


## Vulnerability Assessment & Security Events

Wazuh's vulnerability assessment module is a powerful tool that can be used to periodically scan an agent's operating system for installed applications and their corresponding versions.

Wazuh can use this information, retrieved by the agent, to compare it against a database of CVEs to discover potential vulnerabilities. The vulnerability scanner module will perform a full scan when the Wazuh agent is first [installed](wazuh_setup.md#wazuh-agents) on a device and **must** be configured to run at a set interval afterwards. 

!!! note
    By default it is set to 5 minute intervals using the following configuration

    ```xml
    <vulnerability-detector>
        <enabled>no</enabled>
        <interval>5m</interval>
        <ignore_time>6h</ignore_time>
        <run_on_start>yes</run_on_start>
    ```

Wazuh is also capable of testing an agent's configuration against certain rulesets to check for compliance. These compliance checks are usually very sensitive and a lot of events will be recorded.