#! /bin/bash

echo "查找待清理目标..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~"  

echo "开始清除..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~" -o -name "1" | xargs rm -fr

echo "清理后确认..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~" 

echo "complate!"


