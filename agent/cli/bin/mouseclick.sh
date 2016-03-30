#!/bin/sh
# usage mouseclick.sh <wid> <screenshot> PATTERN_FILES...
# use wid 0 for desktop icons
# used commands
xte_command=$(which xte)
visgrep_command=$(which visgrep)
xwininfo_command=$(which xwininfo)

wid=$1
shift
windowimg=$1
shift
mousemove=1

if [ -n "$xte_command" ]; then
	# search for a pattern
	#rpos=`${visgrep_command} $windowimg $pattern $pattern`
	for pattern in $@
		do
		mousemove=1
		rpos=$($visgrep_command $windowimg $pattern)
		if [ "$wid" -eq "0" -a -n "$rpos" ]; then		
			# get pattern position (whole desktop)
			x2=$(echo $rpos | sed "s/\(.*\),.*/\1/")
			y2=$(echo $rpos | sed "s/.*,\(.*\) -1/\1/")

			# calculate resulting position (add '10' to be inside)
			x=$(expr $x2 + 10)
			y=$(expr $y2 + 10)
	
			echo Found pattern at screen location x=$x, y$y
			# minimize all windows			
			# wmctrl -k off
			$xte_command "mousemove $x $y" "sleep 1" "mouseclick 1" "sleep 1"
			mousemove=0
		elif [ -n "$rpos" -a -n "$xwininfo_command" ]; then
			# get window position
			x1=$($xwininfo_command -id $wid | awk '/Absolute upper-left X/ {print $NF}')
			y1=$($xwininfo_command -id $wid | awk '/Absolute upper-left Y/ {print $NF}')
			#debug#echo x1=$x1 y1=$y1

			# get found pattern position (inside window)
			x2=$(echo $rpos | sed "s/\(.*\),.*/\1/")
			y2=$(echo $rpos | sed "s/.*,\(.*\) -1/\1/")
			#debug#echo x2=$x2 y2=$y2

			# calculate resulting position (add '10' to be inside)
			x=$(expr $x1 + $x2 + 10)
			y=$(expr $y1 + $y2 + 10)
	
			echo Found pattern at screen location x=$x, y$y

			$xte_command "mousemove $x $y" "sleep 1" "mouseclick 1" "sleep 1"
			mousemove=0
		fi
	done
else
	echo "required commands not installed."
fi

if [ $mousemove -gt 0 ] ; then
	echo "Pattern was not found."
fi

exit $mousemove
