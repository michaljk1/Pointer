#!/usr/bin/bash
DIRECTORY=$1
COMPILE_COMMAND=$2
cd $DIRECTORY
$COMPILE_COMMAND
exit 0