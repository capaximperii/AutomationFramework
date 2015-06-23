#!/bin/sh
#usage: windowinfo.sh <window title>

title=$1

if test $# -eq 0 ; then                    # $# contains the argument count
	echo "window title not specified"
	exit 0
fi

for id in $(xprop -root | grep '_NET_CLIENT_LIST_STACKING(WINDOW)' | cut "-d#" -f2|sed -e 's/,//g') ;
	do
	if /usr/bin/xwininfo -id $id | /bin/grep -i "$1">/dev/null 2>&1 
	then /usr/bin/xwininfo -id $id | /usr/bin/awk '/^xwininfo/ {
			id=$4; title=$0; gsub(/^[^"]+/, "", title);} /-geometry/ { geo=$2; }
			END { print "created window with id " id" and geometry "geo" and title "title }' ;
	fi
done
