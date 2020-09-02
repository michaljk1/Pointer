#!/usr/bin/bash
DIRECTORY=$1
INPUTFILE=$2
OUTPUT_TEACHER=$3
RUN_COMMAND=$4
OUTPUT_STUDENT=$5
cd $DIRECTORY
$RUN_COMMAND < ${INPUTFILE} > ${OUTPUT_STUDENT}
# -B - ignore empty lines
SCORE=$(diff -B ${OUTPUT_TEACHER} ${OUTPUT_STUDENT})
if ! [ -z "$SCORE" ]
then
  exit 1
else
  exit 0
fi

