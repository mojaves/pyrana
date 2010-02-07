#!/bin/bash

function die() 
{
	echo $1 1>&2
	exit 1
}

if [ ! -h pyrana ]; then
	[ -f ../build/lib*/pyrana.so ] || die "build pyrana first!"
	ln -s ../build/lib*/pyrana.so .
fi

export PATH=".:$PATH"
eval $@

if [ -h pyrana.so ]; then
	rm -f pyrana.so
fi

