#! /bin/bash

echo "���Ҵ�����Ŀ��..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~"  

echo "��ʼ���..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~" -o -name "1" | xargs rm -fr

echo "�����ȷ��..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~" 

echo "complate!"


