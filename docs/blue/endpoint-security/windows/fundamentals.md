# Windows OS fundamentals

## Core Windows Processes

You can use the **Task Manager**, a built-in Windows tool, to understand the underlying processes inside a Windows machine. The Task Manager is a GUI-based Windows utility which provides an overview on what is running on the Windows system. It additionally provides information on resource usage, such as how much each process utilizes CPU and memory. You can also terminate processes using the Task Manager.

![Task Manager - Details View](images/taskmanager.png)

The following processes are Core Windows processes and them running is considered to be normal behavior:

- **System**
- **System**
  
  -  -> **smss.exe**

- **crss.exe**
- **wininit.exe**

  - -> **services.exe**

    - -> **svhost.exe**

- **lsass.exe**
- **winlogon.exe**
- **explorer.exe**

!!! note
    The **->** symbol represents a parent-child relationship: **smss.exe** is a child process of **System**

Except the **System** process, no process that isn't depicted with a parent process should have one. The **System** process can only have the **System Idle Process (0)** as its parent.

## Sysinternals

The **Sysinternals** tools are a compilation of over 70 Windows-based tools. Each of these tools falls into one of these categories:

- File and Disk utilities
- Networking utilities
- Process utilities
- Security utilities
- System Information
- Miscellaneous

Two very useful tools for endpoint investigation are:

- **TCPVIEW** -> Networking Utility tool
- **Process Explorer** -> Process Utility tool

### TCPVIEW

This tool is a Windows program that provides a detailed listings of all TCP and UDP endpoints on a Windows system, including the local and remote addresses and state of TCP connections. TCPView offers a more informative and conveniently presented subset of the **Netstat** program which is bundled with Windows. The TCPView download also includes **Tcpvcon**, a CLI version with the same functionality.

### Process Explorer

This tool consists of 2 sub-windows which are displayed. The top windows always shows a list of the currently active processes, including the names of their owning accounts, whereas the information displayed in the bottom windows depends on the mode that the **Process Explorer** is in. 

- **Handle Mode**: This mode provides a view into the handles that a selected process in the top windows has opened
- **DLL Mode**: This mode allows you to see the DLLs and memory-mapped files that the process has loaded

The Process Explorer enables you to inspect the details of a running process like:

- Associated services
- Invoked network traffic
- Handles such as files or directories opened
- DLLs and memory-mapped files loaded

## Logging and Monitoring

### Windows Event Log

Windows event logs are not simple text files and therefore can't be viewed using a text editor. The raw data however can be translated into XML using the Windows API. The events in these log files are stored in a proprietary format with the **.evt** or **.evtx** extension. (1) These files are usually located in `C:\Windows\System32\winevt\Logs`.
{ .annotate }

1. **.evtx**-files are Windows XML event log files. 

There are 3 main way of accessing these event logs within Windows:

1. **EvenViewer**: GUI-based application
2. **Wevtutil.exe**: CLI-based tool
3. **Get-WinEvent**: PowerShell cmdlet

![Windows Event Viewer](images/eventviewer.png)

### Sysmon

Sysmon is a tool to monitor and log events on Windows and commonly used by enterprises and businesses as part of their monitoring and logging solutions. It is part of the Windows [**Sysinternals**](#sysinternals) package, and therefore similar to Windows Event Logs with further detail and granular control.

Sysmon gathers detailed and high-quality logs as well as event tracing that assists in identifying anomalies in a given environment. It is often used with a SIEM or other log parsing solutions that aggregate, filter and visualize events. It includes 27 types of Event IDs, all of which can be used within the required configuration file to specify how the events should be handled and analyzed. You can find an example configuration file [here](https://github.com/SwiftOnSecurity/sysmon-config).

### OSQuery

OSQuery is an open-source tool created by Facebook. It is used to query one or multiple endpoints using SQL syntax. Besides Windows it also runs on Linux, macOS and FreeBSD. To interact with OSQuery usage of the **CMD** or **PowerShell**.

### Wazuh

Wazuh is an open-source, freely available and extensive EDR solution for environments of all sizes. It operates on a management and agent model where a dedicated manager device is responsible for managing agents installed on devices that need to be monitored.

As an EDR, Wazuh is responsible for the following tasks:

- Auditing a device for common vulnerabilities.
- Proactively monitoring a device for suspicious activity such as unauthorized logins, brute-force attacks or privilege escalations
- Visualizing complex data and events into neat and trendy graphs
- Recording a device's normal operating behavior to help detecting anomalies

