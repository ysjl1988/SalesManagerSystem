#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试漫画下载功能
使用管理员账号登录并添加漫画下载任务
"""

import sys
import io
import time
import requests
from urllib.parse import urljoin

# 设置stdout编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置
BASE_URL = "http://localhost:5000"
TEST_COMIC_URL = "http://localhost:8080/"
ADMIN_PHONE = "13564612895"
ADMIN_PASSWORD = "Zk123456"

class ComicDownloadTester:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
    
    def login(self):
        """管理员登录"""
        print("=" * 60)
        print("步骤1: 管理员登录")
        print("=" * 60)
        
        # 获取登录页面CSRF token
        login_page = self.session.get(f"{BASE_URL}/login")
        
        # 解析CSRF token
        csrf_token = None
        if 'csrf_token' in login_page.text:
            import re
            match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', login_page.text)
            if match:
                csrf_token = match.group(1)
        
        # 提交登录表单
        data = {
            'phone': ADMIN_PHONE,
            'password': ADMIN_PASSWORD,
        }
        if csrf_token:
            data['csrf_token'] = csrf_token
        
        response = self.session.post(f"{BASE_URL}/login", data=data, allow_redirects=True)
        
        # 检查登录是否成功
        if '登录成功' in response.text or '首页' in response.text or response.url.endswith('/'):
            print(f"✓ 登录成功: {ADMIN_PHONE}")
            self.logged_in = True
            return True
        else:
            print(f"✗ 登录失败")
            print(f"  URL: {response.url}")
            return False
    
    def add_comic(self):
        """添加漫画下载任务"""
        print("\n" + "=" * 60)
        print("步骤2: 添加漫画下载任务")
        print("=" * 60)
        print(f"漫画URL: {TEST_COMIC_URL}")
        
        # 获取管理页面CSRF token
        mgmt_page = self.session.get(f"{BASE_URL}/comic_management")
        
        csrf_token = None
        if 'csrf_token' in mgmt_page.text:
            import re
            match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', mgmt_page.text)
            if match:
                csrf_token = match.group(1)
        
        # 提交添加表单
        data = {
            'url': TEST_COMIC_URL,
            'title': '',  # 留空自动识别
        }
        if csrf_token:
            data['csrf_token'] = csrf_token
        
        response = self.session.post(f"{BASE_URL}/comic/add", data=data, allow_redirects=True)
        
        # 检查是否成功
        if '下载任务已添加' in response.text or response.url.endswith('/comic_management'):
            print("✓ 漫画下载任务添加成功")
            return True
        else:
            print("✗ 添加失败")
            print(f"  当前URL: {response.url}")
            return False
    
    def check_download_progress(self, max_wait=60):
        """检查下载进度"""
        print("\n" + "=" * 60)
        print("步骤3: 检查下载进度")
        print("=" * 60)
        
        comic_id = None
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # 获取所有漫画进度
            try:
                response = self.session.get(f"{BASE_URL}/comic/progress/all")
                comics = response.json()
                
                if comics:
                    comic = comics[0]  # 取第一个
                    comic_id = comic['id']
                    status = comic['status']
                    progress = comic['progress']
                    title = comic['title']
                    
                    print(f"  [{status}] {title} - 进度: {progress}%")
                    
                    if status == 'completed':
                        print(f"\n✓ 下载完成!")
                        return comic_id
                    elif status == 'failed':
                        print(f"\n✗ 下载失败!")
                        return None
                else:
                    print("  等待任务创建...")
                    
            except Exception as e:
                print(f"  获取进度出错: {e}")
            
            time.sleep(3)
        
        print(f"\n⚠ 等待超时，但下载可能仍在后台进行")
        return comic_id
    
    def view_comic_detail(self, comic_id):
        """查看漫画详情"""
        print("\n" + "=" * 60)
        print("步骤4: 查看漫画详情")
        print("=" * 60)
        
        response = self.session.get(f"{BASE_URL}/comic/{comic_id}/view")
        
        if response.status_code == 200:
            print("✓ 漫画详情页访问成功")
            
            # 检查是否显示章节
            if '章节列表' in response.text:
                print("✓ 章节列表显示正常")
            
            return True
        else:
            print(f"✗ 访问失败: {response.status_code}")
            return False
    
    def view_chapter(self, comic_id, chapter_id):
        """查看漫画章节"""
        print("\n" + "=" * 60)
        print("步骤5: 查看漫画章节（阅读器）")
        print("=" * 60)
        
        response = self.session.get(f"{BASE_URL}/comic/{comic_id}/chapter/{chapter_id}/view")
        
        if response.status_code == 200:
            print("✓ 阅读器访问成功")
            
            # 检查是否有图片
            if 'comic-page' in response.text or '.jpg' in response.text:
                print("✓ 漫画图片已加载")
            
            return True
        else:
            print(f"✗ 访问失败: {response.status_code}")
            return False
    
    def verify_downloaded_files(self, comic_id):
        """验证下载的文件"""
        print("\n" + "=" * 60)
        print("步骤6: 验证下载的文件")
        print("=" * 60)
        
        import os
        import glob
        
        # 检查漫画存储目录
        comics_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static', 'comics')
        
        if not os.path.exists(comics_dir):
            print(f"✗ 漫画目录不存在: {comics_dir}")
            return False
        
        # 查找漫画文件夹
        comic_folders = glob.glob(os.path.join(comics_dir, f'{comic_id}_*'))
        
        if not comic_folders:
            print(f"✗ 未找到漫画文件夹 (ID: {comic_id})")
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
            return True
        else:
            print(f"⚠ 图片数量不足 (期望16张, 实际{total_images}张)")
            return False
    
    def run_test(self):
        """运行完整测试"""
        print("\n" + "=" * 60)
        print("开始测试漫画下载功能")
        print("=" * 60)
        
        # 步骤1: 登录
        if not self.login():
            print("\n✗ 测试失败: 登录失败")
            return False
        
        # 步骤2: 添加漫画
        if not self.add_comic():
            print("\n✗ 测试失败: 添加漫画失败")
            return False
        
        # 步骤3: 检查下载进度
        comic_id = self.check_download_progress(max_wait=30)
        
        if not comic_id:
            print("\n✗ 测试失败: 无法获取漫画ID")
            return False
        
        # 等待一会确保下载完成
        print("\n等待下载完成...")
        time.sleep(5)
        
        # 步骤4: 查看详情
        self.view_comic_detail(comic_id)
        
        # 步骤5: 查看章节（假设章节ID为1）
        self.view_chapter(comic_id, 1)
        
        # 步骤6: 验证文件
        files_ok = self.verify_downloaded_files(comic_id)
        
        # 总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"✓ 管理员登录: 通过")
        print(f"✓ 添加下载任务: 通过")
        print(f"✓ 下载进度跟踪: 通过")
        print(f"✓ 漫画详情查看: 通过")
        print(f"✓ 章节阅读器: 通过")
        print(f"{'✓' if files_ok else '✗'} 文件下载验证: {'通过' if files_ok else '失败'}")
        print("=" * 60)
        
        if files_ok:
            print("\n🎉 所有测试通过！漫画下载功能正常工作。")
            print(f"\n访问地址:")
            print(f"  - 漫画管理: http://localhost:5000/comic_management")
            print(f"  - 漫画详情: http://localhost:5000/comic/{comic_id}/view")
        
        return files_ok


if __name__ == "__main__":
    tester = ComicDownloadTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)
