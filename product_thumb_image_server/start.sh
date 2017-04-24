#!/bin/bash                                                                                                                  

. /etc/profile
. ~/.bash_profile

cd /home/xiongzhenqian/apps/tmall_fcy_detail
bin=tmall_fcy_detail_main.py

Bin=${bin}

PName=`ps -ef | grep ${Bin} | grep -v grep | awk '{print $8}'`

if [ ! ${PName} ] ; then
    echo "[INFO] `date +'%Y-%m-%d %H:%M:%S'` start server[${bin}]"
    nohup /usr/bin/xvfb-run /usr/local/bin/python ${bin} 2>&1 >>run.log &
    #else
    #echo "[ERROR] can not start server[${bin}],because have others server[${PName}] started"
fi

