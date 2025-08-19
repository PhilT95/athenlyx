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

## Windows Process - System

The **System** process, which always gets the PID 4, is a special kind of thread that runs only in *kernel-mode*. System threads have all attributes and contexts of regular *user-mode* threads[^1] but are different in that they run only in kernel-mode executing code loaded in system space like loading device drivers. In addition, system threads don't have a user process address space and hence must allocate any dynamic storage from OS memory heaps, such as a paged or nonpaged pool. If you want to know more about *kernel mode* and *user mode* follow [this](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/user-mode-and-kernel-mode) link.

[^1]: Such as a hardware context, priority and more


=== "Process Explorer"


    Using the **Process Explorer** tool, you can view these properties and we can identify the normal behavior of this process.

    ![System Properties using Process Explorer](images/process_system-properties.png)


    The important information for this process is:

    - **Image Path**: N/A
    - **Parent Process**: None
    - **Number of Instances**: One
    - **User Account**: Local System
    - **Start Time**: At boot time


=== "System Informer"

    If you use the **System Informer** tool, the information looks a bit different.

    ![System properties using System Informer](images/process_system-propertiesSI.png)

    The important information that you can see here, which is different from the one provided by the Process Explorer, is:

    - **Image Path**: ``C:\Windows\system32\ntoskrnl.exe``
    - **Parent Process**: System Idle Process (0)

    Using this information, unusual behavior for this process would be:

    - Having a parent process aside from the *System Idle Process (0)*
    - Multiple instances of System, because it should only be one
    - A different PID instead of 4
    - Not running in Session 0
