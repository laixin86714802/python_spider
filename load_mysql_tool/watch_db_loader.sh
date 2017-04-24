#!/bin/bash


cd /home/linuxer/FtpServer/GhLoad2Mysql
predate=`date +%Y%m%d`

while :
do
    bash start_all.sh
    sleep 30
done

