#!/usr/bin/env bash
#arguments: solution_dir, program_name, input name, output name, number of compile command words, number of run command words, compile command, run command
#sample: ./run.sh solution_dir zadanie1.cpp zad1_input.txt zad1_output.txt 0 2 python pajton.py
#uruchamianie: ./run.sh solution_dir zadanie1.cpp zad1_input.txt zad1_output.txt 2 1 g++ zadanie1.cpp ./a.out
#uruchamianie: ./run.sh solution_dir dzawa.java zad1_input.txt zad1_output.txt 2 2 javac dzawa.java java Start
DIRECTORY=$1
cd $DIRECTORY
PROG2TEST=$2
INPUTFILE=$3
OUTPUTFILE=$4
COMPILE_ARGS=$5
RUN_ARGS=$6
COMPILE_COMMAND="${@:7:$COMPILE_ARGS}"
RUN_POSITION=$(( $RUN_ARGS*-1 ))
RUN_COMMAND="${@: $RUN_POSITION}"
$COMPILE_COMMAND
$RUN_COMMAND ${PROG2TEST} < ${INPUTFILE} > ${PROG2TEST}_output_student.txt
SCORE=$(diff ${OUTPUTFILE} ${PROG2TEST}_output_student.txt)
if ! [ -z "$SCORE" ]
then
	echo $SCORE
fi

