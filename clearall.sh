#! /bin/bash

echo "���Ҵ�����Ŀ��..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~" -o -name "*.html" -o -name "*.un~"

echo "��ʼ���..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~"  -o -name "*.html"  -o -name "*.un~" | xargs rm -fr

echo "������ȷ��..."
find ./ -name  "*.pyc" -o -name "*.log" -o -name "*.un~" -o -name "*.html"  -o -name "*.un~"

echo "complate!"

