#!/usr/bin/env bash
DIRECTORY=$1
cd $DIRECTORY
PROG2TEST=$2
INPUTFILE=$3
OUTPUTFILE=$4
RUN_COMMAND=$5
$RUN_COMMAND ulimit -v 0 ${PROG2TEST}  < ${INPUTFILE} > ${PROG2TEST}_output_student.txt
SCORE=$(diff ${OUTPUTFILE} ${PROG2TEST}_output_student.txt)
if ! [ -z "$SCORE" ]
then
	echo $SCORE
fi
exit 0

