# -*- coding: utf-8 -*-
import re

# 读取文件
with open('app/comic_downloader.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到第32-35行并替换
output_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # 找到 cookies 配置行
    if i == 32 and "'cookies': {'cover': '1'}" in line:
        indent = '            '
        output_lines.append(indent + "'cookies': {\n")
        output_lines.append(indent + "    'cover': '1',\n")
        output_lines.append(indent + "    'mg': 'yes',\n")
        output_lines.append(indent + "},\n")
        i += 1
        continue
    # 找到 image_selectors 行，在它之前添加 headers
    elif i == 33 and "'image_selectors'" in line:
        indent = '            '
        output_lines.append(indent + "'headers': {\n")
        output_lines.append(indent + "    'Referer': 'REPLACEME',\n")
        output_lines.append(indent + "},\n")
        output_lines.append(line)
        i += 1
        continue
    else:
        output_lines.append(line)
        i += 1

# 写入文件
with open('app/comic_downloader.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print('Config updated')
