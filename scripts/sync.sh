#!/bin/bash



cd /usr/docs
echo $(date) :  Starting sync with git... >> scripts/sync.log


prev="$(git rev-list HEAD -n 1)"
echo $(date) :  Current git HEAD is  $prev >> scripts/sync.log
git pull --rebase
now="$(git rev-list HEAD -n 1)"
echo $(date) :  New git HEAD after git pull is $now >> scripts/sync.log

if [ "$now" != "$prev" ]; then
	echo $(date) :  Changes detected. Rebuilding web page... >> scripts/sync.log
	cd /usr/docs
	echo $(/home/linuxadmin/.local/bin/mkdocs build) >> scripts/build.log
	cp /usr/docs/site/* /www/ -rf
	echo $(date) :  Sync finalized. >> scripts/sync.log
 else
	echo $(date) : No changes detected. >> scripts/sync.log
fi


