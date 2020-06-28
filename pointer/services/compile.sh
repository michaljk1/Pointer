#!/usr/bin/env bash
#uruchamianie: ./run.sh solution_dir javac dzawa.java
DIRECTORY=$1
cd $DIRECTORY
COMPILE_COMMAND="${@:2}"
$COMPILE_COMMAND
exit 0

