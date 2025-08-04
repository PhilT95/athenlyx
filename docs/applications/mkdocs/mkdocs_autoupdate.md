# Auto-Update using git
Once you set up your server, you usually have to manually update your documentation and build the webpages again on the webserver itself, as well as copying the newly generated files into the web directory. Using **crontab** we can automate this process and you don't have to touch your server again to update your website.

Just create a scripts directory within the git repository and create a new bash file.

```console
[root@machine project]$ mkdir scripts
[root@machine project]$ touch scripts/sync.sh
```

Edit the synch.sh file and add the following lines:

```bash
#!/bin/bash


# Sets the correct working directory
cd /path/to/your/project
echo $(date) :  Starting sync with git... >> scripts/sync.log

# This script checks if a new update has been pulled by comparing the HEAD before and after a git pull --rebase
prev="$(git rev-list HEAD -n 1)"
echo $(date) :  Current git HEAD is  $prev >> scripts/sync.log
git pull --rebase
now="$(git rev-list HEAD -n 1)"
echo $(date) :  New git HEAD after git pull is $now >> scripts/sync.log


# If the HEAD after git pull is different, changes have been downloaded and mkdocs will be used to generate the websites accordingly.
if [ "$now" != "$prev" ]; then
	echo $(date) :  Changes detected. Rebuilding web page... >> scripts/sync.log
	cd /path/to/your/project
	echo $(/home/linuxadmin/.local/bin/mkdocs build) >> scripts/build.log
	cp /path/to/your/project/site/* /path/to/your/webdir -rf
	echo $(date) :  Sync finalized. >> scripts/sync.log
 else
	echo $(date) : No changes detected. >> scripts/sync.log
fi
```

!!! info "Check your paths"
    Please make sure you replace the directory paths with the ones from your setup.