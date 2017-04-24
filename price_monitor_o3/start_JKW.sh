#!/bin/bash                                                                                                                  

. /etc/profile
. ~/.bash_profile

cd /home/xiongzhenqian/apps/price_monitor_o2
bin=PriceMonitorCodeJKW.py

Bin=${bin}

PName=`ps -ef | grep ${Bin} | grep -v grep | awk '{print $8}'`

if [ ! ${PName} ] ; then
    echo "[INFO] `date +'%Y-%m-%d %H:%M:%S'` start server[${bin}]"
    #nohup /usr/bin/xvfb-run python ${bin} 2>&1 >>run.log &
    /usr/bin/xvfb-run /usr/local/bin/python ${bin} 
    #else
    #echo "[ERROR] can not start server[${bin}],because have others server[${PName}] started"
fi

