import pytest
import time
import os
import glob
from playwright.sync_api import Playwright, sync_playwright


class TestComicDownloader:
    """漫画下载管理功能 UAT 测试 (005-comic-downloader)"""
    
    BASE_URL = "http://127.0.0.1:5000"
    TEST_COMIC_URL = "http://127.0.0.1:5000/test_comic/"
    ADMIN_PHONE = "13564612895"
    ADMIN_PASSWORD = "Zk123456"
    
    @pytest.fixture(scope="module")
    def playwright(self) -> Playwright:
        with sync_playwright() as p:
            yield p
    
    @pytest.fixture(scope="module")
    def browser(self, playwright: Playwright):
        browser = playwright.chromium.launch(headless=True, slow_mo=50)
        yield browser
        browser.close()
    
    @pytest.fixture(scope="function")
    def page(self, browser):
        page = browser.new_page(base_url=self.BASE_URL)
        yield page
        page.close()
    
    def _login(self, page, phone, password):
        """通用登录方法"""
        page.goto("/login")
        page.fill("id=phone", phone)
        page.fill("id=password", password)
        page.click("input[type='submit']")
        page.wait_for_url("/")
    
    # ==================== TC1: 权限控制测试 ====================
    
    def test_normal_user_cannot_see_comic_menu(self, page):
        """普通用户登录后看不到"漫画管理"菜单"""
        import random
        phone = f"138{random.randint(10000000, 99999999)}"
        
        page.goto("/register")
        page.fill("id=phone", phone)
        page.fill("id=email", f"test{random.randint(1000,9999)}@test.com")
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_url("/login")
        
        self._login(page, phone, "Test123456")
        
        assert page.locator("a[href='/comic_management']").count() == 0
    
    def test_normal_user_access_comic_management_forbidden(self, page):
        """普通用户直接访问 /comic_management 被重定向到首页"""
        import random
        phone = f"138{random.randint(10000000, 99999999)}"
        
        page.goto("/register")
        page.fill("id=phone", phone)
        page.fill("id=email", f"test{random.randint(1000,9999)}@test.com")
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_url("/login")
        
        self._login(page, phone, "Test123456")
        page.goto("/comic_management")
        
        assert page.url == "http://127.0.0.1:5000/"
        page_content = page.content()
        assert "权限" in page_content or "没有权限" in page_content or "销售管理系统" in page_content
    
    def test_admin_can_see_comic_menu_and_access(self, page):
        """管理员可以看到菜单并正常访问漫画管理页面"""
        self._login(page, self.ADMIN_PHONE, self.ADMIN_PASSWORD)
        
        comic_link = page.locator("a[href='/comic_management']")
        assert comic_link.is_visible()
        assert "漫画管理" in comic_link.inner_text()
        
        page.goto("/comic_management")
        assert page.url == "http://127.0.0.1:5000/comic_management"
        assert "漫画管理" in page.content()
    
    # ==================== TC2: 漫画下载测试 ====================
    
    def test_add_comic_download_task(self, page):
        """管理员添加漫画下载任务，等待下载完成"""
        self._login(page, self.ADMIN_PHONE, self.ADMIN_PASSWORD)
        page.goto("/comic_management")
        
        # 清理之前可能存在的测试漫画
        page_content = page.content()
        while "UI测试-肉包子打狗一去不回" in page_content:
            delete_form = page.locator("form[action*='/comic/'][action*='/delete']").first
            if delete_form.count() > 0 and delete_form.is_visible():
                page.on("dialog", lambda dialog: dialog.accept())
                delete_form.locator("button").click()
                page.wait_for_timeout(1000)
                page.goto("/comic_management")
                page_content = page.content()
            else:
                break
        
        # 添加下载任务
        page.fill("input#url", self.TEST_COMIC_URL)
        page.fill("input#title", "UI测试-肉包子打狗一去不回")
        page.click("button[type='submit']")
        page.wait_for_url("/comic_management")
        
        assert "下载任务已添加" in page.content()
        assert "UI测试-肉包子打狗一去不回" in page.content()
        
        import re
        import sys
        
        # 等待下载完成（最多90秒）
        completed = False
        comic_id = None
        for i in range(30):
            page.goto("/comic_management")
            page_content = page.content()
            
            # 检查状态
            if "已完成" in page_content and "UI测试-肉包子打狗一去不回" in page_content:
                completed = True
                break
            if "下载失败" in page_content and "UI测试-肉包子打狗一去不回" in page_content:
                pytest.fail("漫画下载失败")
            
            time.sleep(3)
        
        assert completed, "下载未在预期时间内完成"
        
        # 从数据库直接获取漫画ID（更可靠）
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        sys.path.insert(0, project_root)
        from app import app as flask_app
        from app.models.comic import Comic
        
        with flask_app.app_context():
            comic = Comic.query.filter(Comic.title.like('%UI测试%')).order_by(Comic.id.desc()).first()
            if comic:
                comic_id = str(comic.id)
        
        assert comic_id is not None, "未能从数据库获取漫画ID"
        
        # 验证本地文件
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        comics_dir = os.path.join(project_root, 'app', 'static', 'comics')
        comic_folders = glob.glob(os.path.join(comics_dir, f'{comic_id}_*'))
        assert len(comic_folders) > 0, "未找到下载的漫画文件夹"
        
        total_images = 0
        for folder in comic_folders:
            chapter_folders = glob.glob(os.path.join(folder, 'chapter_*'))
            for cf in chapter_folders:
                total_images += len(glob.glob(os.path.join(cf, '*.jpg')))
        
        assert total_images >= 16, f"下载图片数量不足，期望>=16，实际{total_images}"
    
    # ==================== TC3: 漫画阅读测试 ====================
    
    def test_comic_reader(self, page):
        """测试漫画阅读器：图片显示、翻页导航"""
        self._login(page, self.ADMIN_PHONE, self.ADMIN_PASSWORD)
        page.goto("/comic_management")
        
        # 查找测试漫画
        view_link = page.locator("a[href*='/comic/'][href*='/view']").first
        assert view_link.count() > 0 and view_link.is_visible(), "没有可查看的漫画"
        
        href = view_link.get_attribute("href")
        parts = [p for p in href.split("/") if p]
        comic_id = parts[1]
        
        # 进入详情页
        view_link.click()
        page.wait_for_url(f"**/comic/{comic_id}/view")
        assert "章节列表" in page.content()
        
        # 点击第一个章节
        chapter_link = page.locator("a.chapter-item").first
        assert chapter_link.count() > 0 and chapter_link.is_visible(), "没有可阅读的章节"
        
        chapter_link.click()
        page.wait_for_load_state("networkidle")
        
        # 验证阅读器页面有图片
        page_content = page.content()
        assert "reader-image" in page_content or ".jpg" in page_content, "阅读器中没有图片"
        
        images = page.locator("img.reader-image")
        assert images.count() > 0, "未找到阅读器图片元素"
    
    # ==================== TC4: 删除功能测试 ====================
    
    def test_delete_comic(self, page):
        """删除漫画，验证数据库记录和本地文件都被清理"""
        self._login(page, self.ADMIN_PHONE, self.ADMIN_PASSWORD)
        page.goto("/comic_management")
        
        view_link = page.locator("a[href*='/comic/'][href*='/view']").first
        assert view_link.count() > 0 and view_link.is_visible(), "没有可删除的漫画"
        
        href = view_link.get_attribute("href")
        comic_id = [p for p in href.split("/") if p][1]
        
        # 记录文件夹路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        comics_dir = os.path.join(project_root, 'app', 'static', 'comics')
        comic_folders_before = glob.glob(os.path.join(comics_dir, f'{comic_id}_*'))
        folder_existed = len(comic_folders_before) > 0
        
        # 提交删除
        delete_form = page.locator(f"form[action='/comic/{comic_id}/delete']").first
        assert delete_form.count() > 0 and delete_form.is_visible(), "未找到删除按钮"
        
        page.on("dialog", lambda dialog: dialog.accept())
        delete_form.locator("button").click()
        page.wait_for_url("/comic_management")
        
        page_content = page.content()
        assert "漫画已删除" in page_content or f"comic/{comic_id}/view" not in page_content, "漫画未从列表中消失"
        
        # 验证文件夹已删除
        if folder_existed:
            comic_folders_after = glob.glob(os.path.join(comics_dir, f'{comic_id}_*'))
            assert len(comic_folders_after) == 0, "漫画文件夹未被删除"
