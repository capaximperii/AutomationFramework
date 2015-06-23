#!/bin/bash
#usage: windowfocus.sh <process name>
XDOTOOL=$(which xdotool)
proc=$1

if [ -z ${XDOTOOL} ]; then
	echo "Command xdotool is not installed"
	exit -1
fi

if [ -z ${XDOTOOL} ]; then
	echo "Command expects process name argument"
	exit -1
fi

focus=1

for p in $(pidof $proc); do
	wid=$($XDOTOOL search --onlyvisible --pid $p 2>/dev/null | head -n 1)
	if [ ${#wid} -gt 0 ] ; then
		$XDOTOOL windowactivate $wid
		echo $wid
		focus=0
	fi
done
if [ $focus -eq 0 ]; then
	echo "Window $proc is in focus"
else
	echo "Window not found"
fi

exit $focus

