#!/bin/bash                                                                                                                  

. /etc/profile
. ~/.bash_profile

cd /data/developer/apps/load_mysql_tool
bin=load_mysql_tool_main.py

Bin=${bin}

PName=`ps -ef | grep ${Bin} | grep -v grep | awk '{print $8}'`

if [ ! ${PName} ] ; then
    echo "[INFO] `date +'%Y-%m-%d %H:%M:%S'` start server[${bin}]"
    #/usr/bin/xvfb-run /usr/local/bin/python ${bin} 
    /usr/local/bin/python ${bin} 
fi

