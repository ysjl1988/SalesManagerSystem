import pytest
from playwright.sync_api import Playwright, sync_playwright


class TestSalesManagerSystem:
    """销售管理系统UAT测试"""
    
    @pytest.fixture(scope="module")
    def playwright(self) -> Playwright:
        """初始化Playwright"""
        with sync_playwright() as p:
            yield p
    
    @pytest.fixture(scope="module")
    def browser(self, playwright: Playwright):
        """初始化浏览器"""
        browser = playwright.chromium.launch(
            headless=True,  # 无头模式运行
            slow_mo=0.5,  # 降低操作速度，便于观察
        )
        yield browser
        browser.close()
    
    @pytest.fixture(scope="function")
    def page(self, browser):
        """初始化页面"""
        page = browser.new_page(
            base_url="http://127.0.0.1:5000"
        )
        yield page
        page.close()
    
    def test_home_page(self, page):
        """测试首页访问"""
        # 访问首页
        page.goto("/")
        
        # 验证页面标题
        assert page.title() == "销售管理系统"
        
        # 验证页面包含"销售管理系统"文本
        assert page.locator("#branding h1").is_visible()
        
        # 验证页面包含登录和注册链接（使用first()避免重复）
        assert page.locator("a[href='/login']").first.is_visible()
        assert page.locator("a[href='/register']").first.is_visible()
    
    def test_register_page(self, page):
        """测试注册页面"""
        # 访问注册页面
        page.goto("/register")
        
        # 验证页面标题
        assert page.title() == "销售管理系统"
        
        # 验证表单元素存在
        assert page.locator("id=phone").is_visible()
        assert page.locator("id=email").is_visible()
        assert page.locator("id=password").is_visible()
        assert page.locator("input[type='submit']").is_visible()
    
    def test_register_functionality(self, page):
        """测试注册功能"""
        import random
        
        # 访问注册页面
        page.goto("/register")
        
        # 生成随机手机号和邮箱
        phone = f"138{random.randint(10000000, 99999999)}"
        email = f"test{random.randint(1000, 9999)}@example.com"
        password = "Test123456"
        
        # 填写注册表单
        page.fill("id=phone", phone)
        page.fill("id=email", email)
        page.fill("id=password", password)
        
        # 提交表单
        page.click("input[type='submit']")
        
        # 验证注册成功并跳转到登录页
        page.wait_for_url("/login")
        assert page.url == "http://127.0.0.1:5000/login"
    
    def test_login_page(self, page):
        """测试登录页面"""
        # 访问登录页面
        page.goto("/login")
        
        # 验证页面标题
        assert page.title() == "销售管理系统"
        
        # 验证表单元素存在
        assert page.locator("id=phone").is_visible()
        assert page.locator("id=password").is_visible()
        assert page.locator("input[type='submit']").is_visible()
    
    def test_login_functionality(self, page):
        """测试登录功能"""
        import random
        
        # 先注册一个用户
        page.goto("/register")
        phone = f"138{random.randint(10000000, 99999999)}"
        email = f"test{random.randint(1000, 9999)}@example.com"
        password = "Test123456"
        page.fill("id=phone", phone)
        page.fill("id=email", email)
        page.fill("id=password", password)
        page.click("input[type='submit']")
        page.wait_for_url("/login")
        
        # 使用注册的手机号和密码登录
        page.fill("id=phone", phone)
        page.fill("id=password", password)
        
        # 提交表单
        page.click("input[type='submit']")
        
        # 验证登录成功并跳转到首页
        page.wait_for_url("/")
        assert page.url == "http://127.0.0.1:5000/"
        
        # 验证首页包含用户管理链接（使用first()避免重复）
        assert page.locator("a[href='/user_management']").first.is_visible()
        assert page.locator("a[href='/logout']").first.is_visible()
    
    def test_user_management(self, page):
        """测试用户管理功能"""
        # 先登录
        self.test_login_functionality(page)
        
        # 访问用户管理页面（使用first()避免重复）
        page.locator("a[href='/user_management']").first.click()
        
        # 验证页面跳转到用户管理页
        page.wait_for_url("/user_management")
        assert page.url == "http://127.0.0.1:5000/user_management"
        
        # 验证页面包含用户列表相关元素
        assert page.locator("th").first.is_visible()
    
    def test_logout(self, page):
        """测试退出登录功能"""
        # 先登录
        self.test_login_functionality(page)
        
        # 点击退出登录（使用first()避免重复）
        page.locator("a[href='/logout']").first.click()
        
        # 验证退出成功并跳转到首页
        page.wait_for_url("/")
        assert page.url == "http://127.0.0.1:5000/"
        
        # 验证页面包含登录和注册链接（使用first()避免重复）
        assert page.locator("a[href='/login']").first.is_visible()
        assert page.locator("a[href='/register']").first.is_visible()
        
        # 验证页面不包含用户管理和退出登录链接
        assert page.locator("a[href='/user_management']").is_hidden()
        assert page.locator("a[href='/logout']").is_hidden()
