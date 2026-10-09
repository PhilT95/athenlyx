# Linux command cheat sheet

A collection of practical commands for everyday work on the Linux command line. Most of them work on every distribution. Where a command only exists on a certain family (RHEL or Debian), it is marked.

Most examples use `sample.txt` as a stand-in for any file you want to work on.

!!! tip
    Every command has a manual. Use `man command` for the full documentation or `command --help` for a short overview.

## Shell basics

|Command|Purpose|Example|
|:------|:------|:------|
|`history`|Show the command history.|`history \| tail -20`|
|`!10`|Run the tenth command in the history.||
|`!!`|Run the previous command again.|`sudo !!`|
|`Ctrl` + `R`|Search the command history interactively.||
|`man`|Open the manual page of a command.|`man ls`|
|`which`|Show the path of an executable.|`which python3`|
|`alias`|Create a shortcut for a command (only for the current session).|`alias ll='ls -lah'`|
|`echo $?`|Show the exit code of the last command. `0` means success.||

## Navigating and managing files

|Command|Purpose|Example|
|:------|:------|:------|
|`pwd`|Print the current directory.||
|`ls -lah`|List files with details, hidden files and human-readable sizes.|`ls -lah /etc`|
|`cd -`|Go back to the previous directory.||
|`cp -r`|Copy files or directories recursively.|`cp -r /etc/nginx /tmp/nginx-backup`|
|`mv`|Move or rename a file.|`mv old.txt new.txt`|
|`rm -r`|Delete a directory and its contents. No recycle bin exists, so double-check the path.|`rm -r /tmp/nginx-backup`|
|`mkdir -p`|Create a directory including missing parent directories.|`mkdir -p /opt/app/config`|
|`ln -s`|Create a symbolic link.|`ln -s /opt/app/config /etc/app`|
|`find`|Search for files by name, type, size, or age.|`find /var/log -name "*.log" -mtime -1`|
|`tree`|Show a directory as a tree. May need to be installed first.|`tree -L 2 /etc`|
|`stat`|Show detailed file information such as size, owner, and timestamps.|`stat sample.txt`|
|`file`|Detect the type of a file.|`file sample.txt`|

## Reading files

|Command|Purpose|Example|
|:------|:------|:------|
|`cat`|Print a file.|`cat sample.txt`|
|`less`|Page through a file. Use `/` to search and `q` to quit.|`less /var/log/messages`|
|`head`|Show the first 10 lines of a file. Use `-n` to change the amount.|`head -n 20 sample.txt`|
|`tail`|Show the last 10 lines of a file.|`tail sample.txt`|
|`tail -f`|Follow a file and print new lines as they are written. Perfect for logs.|`tail -f /var/log/messages`|
|`diff`|Compare two files line by line.|`diff -u old.conf new.conf`|

## Finding and filtering text

These commands are often combined with pipes (`|`), where the output of one command becomes the input of the next.

|Command|Purpose|Example|
|:------|:------|:------|
|`grep`|Filter lines that contain a keyword.|`grep 'error' sample.txt`|
|`grep -i`|Ignore upper and lower case.|`grep -i 'error' sample.txt`|
|`grep -v`|Show only lines that do **not** match.|`grep -v 'debug' sample.txt`|
|`grep -r`|Search through all files in a directory.|`grep -r 'listen' /etc/nginx`|
|`grep -E`|Use extended regular expressions.|`grep -E 'error\|warning' sample.txt`|
|`cut`|Cut a specific field. The default delimiter is a tab, use `-d` to set another one.|`cut -d ':' -f 1 /etc/passwd`|
|`cut -c`|Cut specific characters, for example the first one.|`cut -c1 sample.txt`|
|`sort`|Sort the output alphabetically.|`sort sample.txt`|
|`sort -n`|Sort the output numerically.|`sort -n sample.txt`|
|`uniq`|Remove **adjacent** duplicate lines. Sort the input first.|`sort sample.txt \| uniq`|
|`uniq -c`|Count how often each line occurs.|`sort sample.txt \| uniq -c \| sort -rn`|
|`wc -l`|Count lines.|`wc -l sample.txt`|
|`nl`|Show line numbers.|`nl sample.txt`|
|`tr`|Replace or delete characters.|`echo 'hello' \| tr 'a-z' 'A-Z'`|
|`xargs`|Use the output of a command as arguments for another one.|`find . -name "*.tmp" \| xargs rm`|

## Advanced text processing

|Command|Purpose|Example|
|:------|:------|:------|
|`sed -n`|Print a specific line, for example line 11.|`sed -n '11p' sample.txt`|
|`sed -n`|Print a range of lines, for example 10 to 15.|`sed -n '10,15p' sample.txt`|
|`sed`|Replace text. Add `-i` to change the file directly.|`sed 's/old/new/g' sample.txt`|
|`awk`|Print the lines before line 11.|`awk 'NR < 11 {print $0}' sample.txt`|
|`awk`|Print line 11.|`awk 'NR == 11 {print $0}' sample.txt`|
|`awk`|Print the first and third column. The default delimiter is whitespace.|`awk '{print $1, $3}' sample.txt`|
|`awk -F`|Set a custom delimiter.|`awk -F ':' '{print $1, $7}' /etc/passwd`|

## Users and permissions

|Command|Purpose|Example|
|:------|:------|:------|
|`whoami`|Show the current user.||
|`id`|Show the user ID and group memberships of a user.|`id alice`|
|`sudo`|Run a command with administrator privileges.|`sudo dnf update`|
|`su -`|Switch to the root user with its environment.||
|`useradd`|Create a new user.|`sudo useradd -m -s /bin/bash alice`|
|`passwd`|Set or change the password of a user.|`sudo passwd alice`|
|`usermod -aG`|Add a user to a group. Without `-a` the user is removed from all other groups.|`sudo usermod -aG wheel alice`|
|`chmod`|Change file permissions.|`chmod 640 sample.txt`|
|`chown`|Change owner and group of a file.|`sudo chown alice:alice sample.txt`|
|`last`|Show the last logins.|`last -n 10`|
|`who`|Show who is logged in right now.||

!!! info
    Permissions are written as three digits for **owner**, **group**, and **others**. Each digit is the sum of read (`4`), write (`2`) and execute (`1`). `640` therefore means: owner can read and write, the group can read, everyone else has no access.

## Processes and services

|Command|Purpose|Example|
|:------|:------|:------|
|`ps aux`|List all running processes.|`ps aux \| grep nginx`|
|`top`|Show running processes and resource usage live. `htop` is a more comfortable alternative.||
|`kill`|Stop a process by its ID. Use `-9` only if a normal stop does not work.|`kill 1234`|
|`pkill`|Stop processes by name.|`pkill nginx`|
|`systemctl status`|Show the state of a service.|`systemctl status sshd`|
|`systemctl start` / `stop` / `restart`|Start, stop, or restart a service.|`sudo systemctl restart sshd`|
|`systemctl enable --now`|Start a service and enable it at boot.|`sudo systemctl enable --now nginx`|
|`systemctl list-units --failed`|List all failed services.||

## Logs

|Command|Purpose|Example|
|:------|:------|:------|
|`journalctl -u`|Show the logs of a service.|`journalctl -u sshd`|
|`journalctl -f`|Follow the system journal live.|`journalctl -u sshd -f`|
|`journalctl --since`|Show logs from a certain time.|`journalctl --since "1 hour ago"`|
|`journalctl -p err`|Show only errors and worse.|`journalctl -p err -b`|
|`dmesg`|Show kernel messages, for example hardware, and driver problems.|`sudo dmesg \| tail`|

## Disk and system information

|Command|Purpose|Example|
|:------|:------|:------|
|`df -h`|Show free and used space of all file systems.||
|`du -sh`|Show the size of a directory.|`du -sh /var/log`|
|`du -h --max-depth=1`|Show the size of every directory one level below. Add `\| sort -h` to find the biggest ones.|`du -h --max-depth=1 /var \| sort -h`|
|`lsblk`|List disks and partitions.||
|`free -h`|Show memory usage.||
|`uptime`|Show how long the system is running and the load average.||
|`uname -a`|Show kernel and system information.||
|`cat /etc/os-release`|Show the distribution and its version.||
|`hostnamectl`|Show or change the hostname and system information.||

## Networking

|Command|Purpose|Example|
|:------|:------|:------|
|`ip a`|Show network interfaces and IP addresses.||
|`ip route`|Show the routing table.||
|`ss -tulpn`|Show listening TCP and UDP ports and the process that uses them.|`sudo ss -tulpn \| grep :443`|
|`ping`|Check if a host is reachable. Use `-c` to limit the number of packets.|`ping -c 4 athenlyx.com`|
|`dig`|Query DNS records. Part of `bind-utils` (RHEL) or `dnsutils` (Debian).|`dig athenlyx.com A +short`|
|`traceroute`|Show the path packets take to a host.|`traceroute athenlyx.com`|
|`ssh`|Connect to a remote host.|`ssh alice@192.168.1.10`|
|`scp`|Copy files over SSH.|`scp sample.txt alice@192.168.1.10:/tmp/`|
|`rsync -avz`|Synchronize directories efficiently, locally, or over SSH.|`rsync -avz /opt/app/ alice@192.168.1.10:/opt/app/`|

## Web requests
<!-- vale Vale.Terms = NO -->

|Command|Purpose|Example|
|:------|:------|:------|
|`curl`|Send a web request.|`curl https://athenlyx.com`|
|`curl -I -s`|Send a web request and only get the response header.|`curl -I -s https://athenlyx.com`|
|`curl -L`|Follow redirects.|`curl -L http://athenlyx.com`|
|`curl -o`|Save the response to a file.|`curl -o page.html https://athenlyx.com`|
|`wget`|Download a file.|`wget https://example.com/file.tar.gz`|

<!-- vale Vale.Terms = YES -->

## Package management

|Task|RHEL family (`dnf`)|Debian family (`apt`)|
|:---|:------------------|:--------------------|
|Update package lists|Done automatically|`sudo apt update`|
|Update all packages|`sudo dnf upgrade`|`sudo apt upgrade`|
|Install a package|`sudo dnf install nginx`|`sudo apt install nginx`|
|Remove a package|`sudo dnf remove nginx`|`sudo apt remove nginx`|
|Search for a package|`dnf search nginx`|`apt search nginx`|
|Show package information|`dnf info nginx`|`apt show nginx`|
|Find which package provides a file|`dnf provides /usr/bin/dig`|`dpkg -S /usr/bin/dig`|
|List installed packages|`dnf list installed`|`apt list --installed`|

## Archives and checksums

|Command|Purpose|Example|
|:------|:------|:------|
|`tar -czf`|Create a compressed archive.|`tar -czf backup.tar.gz /opt/app`|
|`tar -tzf`|List the content of an archive without extracting it.|`tar -tzf backup.tar.gz`|
|`tar -xzf`|Extract an archive. Use `-C` to choose the target directory.|`tar -xzf backup.tar.gz -C /tmp`|
|`sha256sum`|Generate the SHA-256 value of a file.|`sha256sum file.txt`|
|`sha256sum -c`|Verify files against a list of checksums.|`sha256sum -c checksums.txt`|
