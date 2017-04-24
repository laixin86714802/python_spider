#!/usr/bin/python
#coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 product_thumb_image_server_main.py
# VERSION: 	 1.0
# CREATED: 	 2016-05-20 10:31
# AUTHOR: 	 xuexiang
# DESCRIPTION:   产品图片获取服务
#
# HISTORY: 
#*************************************************************
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from product_thumb_image_server_class import product_thumb_image_server_class

if __name__ == '__main__':
    app = product_thumb_image_server_class() 
    #20服务器上nginx的web路径
    image_path = "/data/www_resweb"
    app.init(image_path);
    app.service()

