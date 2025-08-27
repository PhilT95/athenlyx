# Sysinternals

The **Sysinternals** tool is a compilation of over 70+ Windows-based tools. These encompass

- **File and Disk utilities**
- **Networking utilities**
- **Process utilities**
- **Security utilities**
- **System Information**
- **Miscellaneous**

The tool is very commonly used for managing Windows systems. It is in fact so popular that even Red Teams and adversaries use them.


## Installation

**Sysinternals** is not a built-in Windows tool, but is provided by Microsoft itself. You can find the entire Sysinternals suite or its single parts [here](https://learn.microsoft.com/en-us/sysinternals/downloads/). YOu can also find out more about the tools used provided by Sysinternals there.

Following the Download of the Sysinternals [ZIP File](https://download.sysinternals.com/files/SysinternalsSuite.zip), you need to extract these files. After the files are extracted, you can also add the folder path to the environment variables of Windows. This allows you to launch these tools from the CMD without navigating to the directory of these tools.

??? tip "Editing Environment variables"
    You can edit environment variables from the **System Properties** Menu. 

    1. You can launch this menu via the CMD by running ``sysdm.cpl``. 
    2. Go to the **Advanced** Tab and click on **Environment Variables...**.
    3. Select **Path** under **System Variables** and select *Edit*. Then press **OK**.
    4. In the new screen, select **New** and enter the folder path where the Sysinternals Suite was extracted to and confirm with OK.

    ![System Properties Menu](images/sysinternals/sysinternals_envmenu.png)

    ![Environment Variables Menu](images/sysinternals/sysinternals_envmenu02.png)

    ![Add Environment Variable Menu](images/sysinternals/sysinternals_envmenu-add.png)

    Now you should be able to run the Sysinternals tools from anywhere using the CMD.

You can also use **Sysinternals** executables directory from the Web without downloading it beforehand. Simply enter a tool's Sysinternals Live path into Windows Explorer or a CMD session as ``\\live.sysinternals.com\tools\<toolname>``. 

!!! note
    To access this web path from your system, you usually need to install and start the WebDAV client on the machine. On most modern Windows machines the client will already be installed, but you need to run it manually. You can start the service from a powershell admin session.

    ```pwsh-session
    PS C:\WINDOWS\system32> Get-Service webclient

    Status   Name               DisplayName
    ------   ----               -----------
    Stopped  WebClient          webclient

    PS C:\WINDOWS\system32> Start-Service webclient
    PS C:\WINDOWS\system32> Get-Service webclient

    Status   Name               DisplayName
    ------   ----               -----------
    Running  WebClient          webclient
    ```

    You also need to enable **Network Discovery**. You can find more about this topic [here](https://support.microsoft.com/en-us/windows/file-sharing-over-a-network-in-windows-b58704b2-f53a-4b82-7bc1-80f9994725bf).




