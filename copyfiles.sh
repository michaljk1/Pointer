#!/usr/bin/bash
PERIOD_SECOND=86400 #seconds per day
TARGET_DIR="/home/backup/"
TMP_DIR=$TARGET_DIR/TMP
INSTANCE_DIR="/home/PycharmProjects/Pointer/instance"
DATABASE="/home/PycharmProjects/Pointer/app.db"
while true; do
#prepare backup
mkdir $TMP_DIR
cp -r $INSTANCE_DIR $TMP_DIR
cp $DATABASE $TMP_DIR

#tar and copy
TAR_FILE=$(date +%Y-%m-%d-%H-%M-%S).tar.gz
tar -zcvf $TAR_FILE $TMP_DIR
cp $TAR_FILE $TARGET_DIR

#clean
rm -r $TMP_DIR
rm $TAR_FILE
sleep $PERIOD_SECOND
done