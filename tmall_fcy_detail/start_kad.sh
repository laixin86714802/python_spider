#!/bin/bash                                                                                                                  

. /etc/profile
. ~/.bash_profile

cd /home/xiongzhenqian/apps/tmall_fcy_detail
bin=tmall_fcy_detail_kad_main.py

Bin=${bin}

PName=`ps -ef | grep ${Bin} | grep -v grep | awk '{print $8}'`

echo "[INFO] `date +'%Y-%m-%d %H:%M:%S'` start server[${bin}]"
nohup /usr/bin/xvfb-run /usr/local/bin/python ${bin}> run_kad.log 2>&1 &

