#!/bin/bash

function die() 
{
	echo $1 1>&2
	exit 1
}

if [ ! -h pyrana ]; then
	[ -d ../build/lib*/pyrana/ ] || die "build pyrana first!"
	ln -s ../build/lib*/pyrana/ .
fi

export PATH=".:$PATH"
eval $@

if [ -h pyrana/ ]; then
	rm -f pyrana/
fi

