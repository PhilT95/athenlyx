![Wazu Banner](images/wazuh_banner.jpg)

# Wazuh - EDR Software Solution

**Wazuh**, created in 2015, is an open-source, freely available and extensive EDR solution. It can be used in all scales of environments. Wazuh operators on a management and agent module. To put it simply, a device is dedicated to running Wazuh called the *manager*. The *agents* are installed on the devices that need to be monitored. 

If you want to install Wazuh and how to configure it have a look at this [Setup Guide](wazuh_setup.md).


## Vulnerability Assessment

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

When everything is configured correctly, each agent will provide an overview of the detected vulnerabilities.

![Agent Vulnerability Dashboard](images/wazuh_agents-vulnerabilities.png)


## Compliance & Policy Auditing

Wazuh has the capabilities to audit and monitor an agent's configuration whilst proactively recording event logs. These audits are performed against a variety of frameworks an legislations such as [NIST](https://www.nist.gov/cyberframework), [MITRE](https://evals.mitre.org/) or [CIS](https://www.cisecurity.org/cis-benchmarks).

![Compliance Audit Based on CIS](images/wazuh_agents-compliance.png)

This Overview shows the percentage on how many checks have been passed by the system, which checks have not and navigating to the **Events** tab gives an insight on events related to settings that were audited.

!!! tip
    While Wazuhs compliance check is a good way to check your systems configuration and hardening level, it usually gives more insight to run the audit manually using tools like [OpenScap](../../servers/linux/hardening/openscap.md).