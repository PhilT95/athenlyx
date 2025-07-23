#!/bin/bash
cd /usr/docs

prev= echo $(git rev-list HEAD -n 1)
git pull --rebase
now= echo $(git rev-list HEAD -n 1)
if [ "$now" = "$prev" ]; then
	mkdocs build
	cp /usr/docs/site/* /www/ -r
fi


