#!/usr/bin/env bash
#uruchamianie: ./run.sh solution_dir javac dzawa.java
DIRECTORY=$1
cd $DIRECTORY
COMPILE_COMMAND="${@:2}"
#$COMPILE_COMMAND 2>compile_error.txt 1>compile_out.txt
#$COMPILE_COMMAND 2>&1 | tee errsdasdsaor.txt
$COMPILE_COMMAND
exit 0
