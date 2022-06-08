#!/bin/bash

for apk in $1/**.apk; do
	outpath=$2/${apk#$1/}
	outpath=${outpath%/*}
	apktool d -sm $apk -out $outpath;
done
