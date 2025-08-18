# Core Windows Processes

Since Windows, as mentioned [here](../index.md) is the most used desktop OS in the world, it is also one of the biggest targets for malware and attacks. Even the newest tools are not 100% effective, so a deeper understanding of normal Windows OS behavior and how you can detect malicious processes running on an endpoint is important.

## Task Manager

The **Task Manager** is a built-in GUI-based Windows utility that enables users to see what is currently running on a given Windows system. It also provides information on resource usage like the CPU and memory utilization by each process. It can also be used to terminate processes.

You can open the Task Manager by right-clicking the Taskbar and selecting *Task Manager*.

![Task Manager](images/taskmanager-detailed.png)

??? tip "Adding more columns"
    The standard columns are usually **Name**,**Status**,**CPU** and **Memory**. You can add and view more columns by right-clicking on any column header to open more options.

    ![Add Columns to Task Manager](images/taskmanager-addcolumn.png)

    The columns you can add are:

    - **Type**: Each process is either an *App*, an *Background process* or an *Windows process*
    - **Publisher**: The author of the program/file
    - **PID**: Windows assigns a unique PID each time a program starts. If the same program has multiple running processes, each will have its unique PID
    - **Process name**: The file name of the process
    - **Command line**: The full command used to launch the process
    - **CPU**: The amount of CPU utilization by the process
    - **Memory**: The amount of physical working memory utilized by the process

    The **Details** tab provides a more detailed view by default.


Since the Task Manager doesn't provide a *parent-child* process view, other tools like the [**System Informer**](https://systeminformer.sourceforge.io/) and [**Process Explorer**](https://learn.microsoft.com/en-us/sysinternals/downloads/process-explorer) can be used.(1)
{ .annotate }

1. The tool *System Informer* was known under the name **Process Hacker**.



