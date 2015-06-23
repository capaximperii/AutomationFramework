#!/bin/bash
#usage: windowimg.sh <outfile> <wid>

xwd_command=$(which xwd)
xwdtopnm_command=$(which xwdtopnm)
pnmtopng_command=$(which pnmtopng)
tmp_file=$(mktemp)

if [ -z $xwd_command -o -z $xwdtopnm_command -o -z $pnmtopng_command ]; then
	echo "Commands are not installed"
	exit 1
fi

if [ -z "$1" ]; then
	echo "command expects an argument for output file"
	exit 1
fi

if [ -n "$2" ] ; then
	echo "clicking for window"
	$xwd_command -id $2 | $xwdtopnm_command | $pnmtopng_command > $tmp_file
else
	$xwd_command -root | $xwdtopnm_command | $pnmtopng_command > $tmp_file
fi

mv $tmp_file $1

