#!/usr/bin/env bash
DIRECTORY=$1
cd $DIRECTORY
COMPILE_COMMAND=$2
$COMPILE_COMMAND
exit 0