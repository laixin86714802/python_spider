#! /bin/bash

echo "���Ҵ�����Ŀ��..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~" -o -name "*.html"

echo "��ʼ���..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~"  -o -name "*.html" | xargs rm -fr

echo "�����ȷ��..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~" -o -name "*.html"

echo "complate!"


