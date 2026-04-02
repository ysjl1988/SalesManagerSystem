#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查阅读页面生成的HTML"""

import sys
import os
import re

os.environ['FLASK_ENV'] = 'testing'
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app, db
from app.models.user import User
from app.session_manager import get_session_manager

with app.app_context():
    with app.test_client() as client:
        # 先登录
        # 获取登录页面的csrf token
        login_page = client.get('/login')
        html = login_page.data.decode('utf-8')
        csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        # 提交登录
        login_data = {
            'phone': '13564612895',
            'password': 'Zk123456',
        }
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        login_resp = client.post('/login', data=login_data, follow_redirects=True)
        print('Login status:', login_resp.status_code)
        
        # 现在访问阅读页面
        resp = client.get('/comic/1/chapter/1/view')
        print('Chapter view status:', resp.status_code)
        
        html = resp.data.decode('utf-8')
        
        # 检查是否有权限错误
        if '权限' in html or '登录' in html:
            print('Warning: Login required or permission denied')
        
        # 查找图片URL
        urls = re.findall(r'src="([^"]*static[^"]*)"', html)
        print('Found', len(urls), 'image URLs')
        for u in urls[:5]:
            print(' ', u)
        
        # 检查是否有空状态提示
        if '暂无图片内容' in html:
            print('\nWarning: Page shows "no content" message')
            # 检查images变量
            if 'images' in html and 'if images' in html:
                print('Template checks for images variable')
        
        # 检查是否有图片错误处理
        if 'onerror' in html:
            print('Image error handling: present')
        
        # 保存HTML用于检查
        with open('chapter_view_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('\nHTML saved to: chapter_view_debug.html')
