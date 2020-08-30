#!/usr/bin/env bash
DIRECTORY=$1
cd $DIRECTORY
PROG2TEST=$2
INPUTFILE=$3
OUTPUT_ADMIN=$4
RUN_COMMAND=$5
OUTPUT_STUDENT=$6
$RUN_COMMAND ${PROG2TEST}  < ${INPUTFILE} > ${OUTPUT_STUDENT}
# -B - ignore empty lines
SCORE=$(diff -B ${OUTPUT_ADMIN} ${OUTPUT_STUDENT})
if ! [ -z "$SCORE" ]
then
  exit 1
else
  exit 0
fi

