#!/bin/bash



cd /usr/docs
echo $(date) ":  Starting sync with git..." >> scripts/sync.log


prev= echo $(git rev-list HEAD -n 1)
echo $(date) ":  Current git HEAD is " $prev >> scripts/sync.log
git pull --rebase
now= echo $(git rev-list HEAD -n 1)
echo $(date) ":  New git HEAD after git pull is " $now >> scripts/sync.log

if [ "$now" = "$prev" ]; then
	echo $(date) ":  Changes detected. Rebuilding web page..." >> scripts/sync.log
	mkdocs build
	cp /usr/docs/site/* /www/ -r
	echo $(date) ":  Sync finalized." >> scripts/sync.log
fi


