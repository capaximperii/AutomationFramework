#!/bin/bash
#usage: windowid.sh <process name>
found=1
wid="No window found"
for p in $(pidof $1); do
	wid=$(xdotool search --onlyvisible --pid $p 2>/dev/null | head -n 1)
	if [ ${#wid} -gt 0 ] ; then
		found=0
		break
	fi
done
echo $wid
exit $found
