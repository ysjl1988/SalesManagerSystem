#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试漫画下载功能
包含：启动测试服务器、添加下载任务、验证下载结果
"""

import sys
import io
import os
import time
import glob
import shutil
import threading
import http.server
import socketserver

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置
TEST_SITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_comic_site')
BASE_URL = "http://localhost:5000"
TEST_PORT = 8080

class TestServer:
    """测试漫画服务器"""
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
    
    def start(self):
        """启动测试服务器（在后台线程中）"""
        os.chdir(TEST_SITE_DIR)
        
        handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer(("", self.port), handler)
        
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        self.running = True
        
        print(f"✓ 测试漫画服务器已启动: http://localhost:{self.port}")
        time.sleep(1)  # 等待服务器启动
    
    def stop(self):
        """停止测试服务器"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("✓ 测试漫画服务器已停止")


def test_download():
    """测试下载流程"""
    import requests
    
    print("\n" + "=" * 60)
    print("步骤1: 管理员登录")
    print("=" * 60)
    
    session = requests.Session()
    
    # 登录
    login_page = session.get(f"{BASE_URL}/login")
    csrf_token = None
    if 'csrf_token' in login_page.text:
        import re
        match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', login_page.text)
        if match:
            csrf_token = match.group(1)
    
    data = {
        'phone': '13564612895',
        'password': 'Zk123456',
    }
    if csrf_token:
        data['csrf_token'] = csrf_token
    
    response = session.post(f"{BASE_URL}/login", data=data, allow_redirects=True)
    if '登录成功' in response.text or '首页' in response.text:
        print("✓ 管理员登录成功")
    else:
        print("✗ 登录失败")
        return False
    
    print("\n" + "=" * 60)
    print("步骤2: 添加漫画下载任务")
    print("=" * 60)
    
    # 获取管理页面
    mgmt_page = session.get(f"{BASE_URL}/comic_management")
    csrf_token = None
    if 'csrf_token' in mgmt_page.text:
        import re
        match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', mgmt_page.text)
        if match:
            csrf_token = match.group(1)
    
    # 添加下载任务
    data = {
        'url': f'http://localhost:{TEST_PORT}/',
        'title': '肉包子打狗一去不回',  # 指定标题，避免自动识别问题
    }
    if csrf_token:
        data['csrf_token'] = csrf_token
    
    response = session.post(f"{BASE_URL}/comic/add", data=data, allow_redirects=True)
    if '下载任务已添加' in response.text:
        print("✓ 漫画下载任务添加成功")
    else:
        print("✗ 添加下载任务失败")
        return False
    
    print("\n" + "=" * 60)
    print("步骤3: 等待下载完成")
    print("=" * 60)
    
    # 等待下载完成
    comic_id = None
    for i in range(20):  # 最多等待60秒
        try:
            response = session.get(f"{BASE_URL}/comic/progress/all")
            comics = response.json()
            
            if comics:
                comic = comics[0]
                comic_id = comic['id']
                status = comic['status']
                progress = comic['progress']
                print(f"  [{status}] 进度: {progress}%")
                
                if status == 'completed':
                    print("✓ 下载完成!")
                    break
                elif status == 'failed':
                    print("✗ 下载失败!")
                    return False
        except Exception as e:
            print(f"  获取进度出错: {e}")
        
        time.sleep(3)
    
    if not comic_id:
        print("✗ 无法获取漫画ID")
        return False
    
    print("\n" + "=" * 60)
    print("步骤4: 验证下载的文件")
    print("=" * 60)
    
    # 检查文件
    comics_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static', 'comics')
    
    if not os.path.exists(comics_dir):
        print(f"✗ 漫画目录不存在: {comics_dir}")
        return False
    
    # 查找漫画文件夹
    comic_folders = glob.glob(os.path.join(comics_dir, f'{comic_id}_*'))
    
    if not comic_folders:
        print(f"✗ 未找到漫画文件夹 (ID: {comic_id})")
        # 列出目录内容
        print(f"  目录内容: {os.listdir(comics_dir) if os.path.exists(comics_dir) else 'N/A'}")
        return False
    
    comic_folder = comic_folders[0]
    print(f"✓ 找到漫画文件夹: {os.path.basename(comic_folder)}")
    
    # 检查章节文件夹
    chapter_folders = glob.glob(os.path.join(comic_folder, 'chapter_*'))
    print(f"✓ 找到 {len(chapter_folders)} 个章节文件夹")
    
    # 统计图片数量
    total_images = 0
    for chapter_folder in chapter_folders:
        images = glob.glob(os.path.join(chapter_folder, '*.jpg'))
        total_images += len(images)
        print(f"  - {os.path.basename(chapter_folder)}: {len(images)} 张图片")
    
    print(f"\n✓ 总共下载了 {total_images} 张图片")
    
    if total_images >= 16:
        print("✓ 图片数量符合预期 (>=16张)")
        success = True
    else:
        print(f"⚠ 图片数量不足 (期望16张, 实际{total_images}张)")
        success = False
    
    print("\n" + "=" * 60)
    print("步骤5: 验证阅读功能")
    print("=" * 60)
    
    # 访问详情页
    response = session.get(f"{BASE_URL}/comic/{comic_id}/view")
    if response.status_code == 200 and '章节列表' in response.text:
        print("✓ 漫画详情页访问成功")
    else:
        print(f"✗ 漫画详情页访问失败: {response.status_code}")
        success = False
    
    # 访问阅读页（需要知道章节ID）
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from app import app
    from app.models.comic import ComicChapter
    
    with app.app_context():
        chapter = ComicChapter.query.filter_by(comic_id=comic_id).first()
        if chapter:
            response = session.get(f"{BASE_URL}/comic/{comic_id}/chapter/{chapter.id}/view")
            if response.status_code == 200:
                print("✓ 阅读器访问成功")
                if '.jpg' in response.text or 'comic-page' in response.text:
                    print("✓ 漫画图片在阅读器中显示")
                else:
                    print("⚠ 阅读器中未检测到图片")
            else:
                print(f"✗ 阅读器访问失败: {response.status_code}")
                success = False
        else:
            print("✗ 未找到章节")
            success = False
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if success:
        print("\n🎉 所有测试通过！漫画下载功能正常工作。")
        print(f"\n访问地址:")
        print(f"  - 漫画管理: http://localhost:5000/comic_management")
        print(f"  - 漫画详情: http://localhost:5000/comic/{comic_id}/view")
        return True
    else:
        print("\n⚠ 部分测试未通过，请检查日志")
        return False


def main():
    print("=" * 60)
    print("开始完整测试漫画下载功能")
    print("=" * 60)
    
    # 启动测试服务器
    server = TestServer(port=TEST_PORT)
    server.start()
    
    try:
        # 运行测试
        success = test_download()
    finally:
        # 停止测试服务器
        server.stop()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
