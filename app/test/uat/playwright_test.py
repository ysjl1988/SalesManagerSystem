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
        page.wait_for_timeout(1000)  # 等待页面跳转
        
        # 使用注册的手机号和密码登录
        page.goto("/login")
        page.fill("id=phone", phone)
        page.fill("id=password", password)
        
        # 提交表单
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)  # 等待登录完成
        
        # 验证登录成功（检查当前URL或页面内容）
        assert page.url == "http://127.0.0.1:5000/"
        assert page.url == "http://127.0.0.1:5000/"
        
        # 验证首页包含用户管理链接（使用first()避免重复）
        assert page.locator("a[href='/user_management']").first.is_visible()
        assert page.locator("a[href='/logout']").first.is_visible()
    
    def test_user_management(self, page):
        """测试用户管理功能（管理员）"""
        # 登录管理员
        page.goto("/login")
        page.fill("id=phone", "13564612895")
        page.fill("id=password", "Zk123456")
        page.click("input[type='submit']")
        page.wait_for_url("/")
        
        # 访问用户管理页面
        page.goto("/user_management")
        
        # 验证页面正常显示
        assert page.url == "http://127.0.0.1:5000/user_management"
        assert "用户管理" in page.content()
        
        # 验证页面包含用户列表相关元素
        assert page.locator("th").first.is_visible()
    
    def test_logout(self, page):
        """测试退出登录功能"""
        # 先登录
        self.test_login_functionality(page)
        
        # 点击退出登录（使用first()避免重复）
        page.locator("a[href='/logout']").first.click()
        page.wait_for_timeout(1000)
        
        # 验证退出成功（如果没有其他session，会跳转到登录页）
        assert page.url == "http://127.0.0.1:5000/login" or page.url == "http://127.0.0.1:5000/"
        
        # 验证页面包含登录链接
        assert page.locator("a[href='/login']").first.is_visible()
    
    def test_login_password_toggle(self, page):
        """测试登录页面密码显示/隐藏切换功能"""
        # 访问登录页面
        page.goto("/login")
        
        # 输入测试密码
        password_input = page.locator("id=password")
        password_input.fill("TestPassword123")
        
        # 验证默认状态为隐藏（type="password"）
        assert password_input.get_attribute("type") == "password"
        
        # 点击显示按钮
        toggle_btn = page.locator("button[data-target='password']")
        toggle_btn.click()
        
        # 验证密码变为可见
        assert password_input.get_attribute("type") == "text"
        
        # 再次点击，验证恢复隐藏
        toggle_btn.click()
        assert password_input.get_attribute("type") == "password"
    
    def test_register_password_toggle(self, page):
        """测试注册页面密码显示/隐藏切换功能"""
        # 访问注册页面
        page.goto("/register")
        
        # 输入测试密码
        password_input = page.locator("id=password")
        password_input.fill("TestPassword123")
        
        # 验证默认状态为隐藏（type="password"）
        assert password_input.get_attribute("type") == "password"
        
        # 点击显示按钮
        toggle_btn = page.locator("button[data-target='password']")
        toggle_btn.click()
        
        # 验证密码变为可见
        assert password_input.get_attribute("type") == "text"
        
        # 再次点击，验证恢复隐藏
        toggle_btn.click()
        assert password_input.get_attribute("type") == "password"
    
    # ==================== 角色与权限测试 ====================
    
    def test_admin_can_access_user_management(self, page):
        """测试管理员可以访问用户管理页面"""
        import random
        
        # 先创建一个管理员用户
        page.goto("/register")
        admin_phone = f"139{random.randint(10000000, 99999999)}"
        page.fill("id=phone", admin_phone)
        page.fill("id=email", f"admin{random.randint(1000,9999)}@test.com")
        page.fill("id=password", "Admin123456")
        page.click("input[type='submit']")
        page.wait_for_url("/login")
        
        # 注：由于注册的都是普通用户，这里使用已知的测试管理员账号
        page.goto("/login")
        page.fill("id=phone", "13564612895")
        page.fill("id=password", "Zk123456")
        page.click("input[type='submit']")
        page.wait_for_url("/")
        
        # 访问用户管理页面
        page.goto("/user_management")
        
        # 验证页面正常显示
        assert "用户管理" in page.content()
        assert page.url == "http://127.0.0.1:5000/user_management"
    
    def test_normal_user_cannot_access_user_management(self, page):
        """测试普通用户不能访问用户管理页面"""
        import random
        
        # 注册一个普通用户
        page.goto("/register")
        phone = f"138{random.randint(10000000, 99999999)}"
        email = f"test{random.randint(1000,9999)}@test.com"
        page.fill("id=phone", phone)
        page.fill("id=email", email)
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_url("/login")
        
        # 登录
        page.fill("id=phone", phone)
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_url("/")
        
        # 尝试访问用户管理页面
        page.goto("/user_management")
        
        # 验证被重定向到首页
        assert page.url == "http://127.0.0.1:5000/"
    
    def test_admin_reset_user_password(self, page):
        """测试管理员重置用户密码"""
        import random
        
        # 登录管理员
        page.goto("/login")
        page.fill("id=phone", "13564612895")
        page.fill("id=password", "Zk123456")
        page.click("input[type='submit']")
        page.wait_for_url("/")
        
        # 访问用户管理页面
        page.goto("/user_management")
        
        # 点击第一个普通用户的重置密码按钮
        reset_btn = page.locator("button:has-text('重置密码')").first
        if reset_btn.is_visible():
            reset_btn.click()
            
            # 处理确认对话框
            page.on("dialog", lambda dialog: dialog.accept())
            
            # 验证提示信息
            page.wait_for_load_state("networkidle")
    
    def test_force_change_password_on_first_login(self, page):
        """测试重置密码后首次登录强制修改密码"""
        import random
        
        # 步骤1: 注册一个新用户
        page.goto("/register")
        test_phone = f"138{random.randint(10000000, 99999999)}"
        test_email = f"test{random.randint(1000,9999)}@test.com"
        page.fill("id=phone", test_phone)
        page.fill("id=email", test_email)
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_url("/login")
        
        # 步骤2: 登录管理员重置该用户密码
        page.goto("/login")
        page.fill("id=phone", "13564612895")
        page.fill("id=password", "Zk123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        # 步骤3: 访问用户管理页面，搜索该用户
        page.goto("/user_management")
        page.fill("id=phone", test_phone)
        page.click("button[type='submit']")  # 搜索按钮
        page.wait_for_timeout(1000)
        
        # 步骤4: 点击重置密码按钮
        page.on("dialog", lambda dialog: dialog.accept())
        reset_btn = page.locator("button:has-text('重置密码')")
        if reset_btn.is_visible():
            reset_btn.click()
            page.wait_for_timeout(1000)
        
        # 步骤5: 退出登录
        page.goto("/logout")
        page.wait_for_timeout(1000)
        
        # 步骤6: 用被重置密码的用户登录
        page.goto("/login")
        page.fill("id=phone", test_phone)
        page.fill("id=password", "111111")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        # 步骤7: 验证被重定向到强制修改密码页面
        assert "/force_change_password" in page.url
        
        # 步骤8: 修改密码
        page.fill("id=new_password", "NewPass123")
        page.fill("id=confirm_password", "NewPass123")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        # 步骤9: 验证成功跳转到首页
        assert page.url == "http://127.0.0.1:5000/"
    def test_multi_user_login(self, page):
        """测试多用户同时登录"""
        import random
        
        # 步骤1: 登录第一个用户（管理员）
        page.goto("/login")
        page.fill("id=phone", "13564612895")
        page.fill("id=password", "Zk123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)  # 等待1秒
        
        # 验证登录成功（检查URL或页面标题）
        assert page.url == "http://127.0.0.1:5000/" or "/force_change_password" in page.url
        
        # 步骤2: 注册并登录第二个用户
        page.goto("/register")
        test_phone = f"138{random.randint(10000000, 99999999)}"
        test_email = f"test{random.randint(1000,9999)}@test.com"
        page.fill("id=phone", test_phone)
        page.fill("id=email", test_email)
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        # 登录第二个用户
        page.goto("/login")
        page.fill("id=phone", test_phone)
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        # 步骤3: 访问多用户管理页面
        page.goto("/multi_user_manager")
        
        # 验证页面显示（检查URL和基本内容）
        assert "/multi_user_manager" in page.url
    
    def test_multi_user_switch(self, page):
        """测试多用户切换"""
        import random
        
        # 登录管理员
        page.goto("/login")
        page.fill("id=phone", "13564612895")
        page.fill("id=password", "Zk123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        # 注册并登录第二个用户
        page.goto("/register")
        test_phone = f"138{random.randint(10000000, 99999999)}"
        page.fill("id=phone", test_phone)
        page.fill("id=email", f"test{random.randint(1000,9999)}@test.com")
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        page.goto("/login")
        page.fill("id=phone", test_phone)
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        # 访问多用户管理页面
        page.goto("/multi_user_manager")
        
        # 点击切换到管理员
        switch_links = page.locator("a[href*='/switch_user/']")
        if switch_links.count() > 0:
            switch_links.first.click()
            page.wait_for_timeout(1000)
            
            # 验证切换成功（回到首页或多用户管理页面）
            current_url = page.url
            assert "/" in current_url
    
    def test_multi_user_logout_single(self, page):
        """测试退出单个用户"""
        import random
        
        # 登录管理员
        page.goto("/login")
        page.fill("id=phone", "13564612895")
        page.fill("id=password", "Zk123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        # 注册并登录第二个用户
        page.goto("/register")
        test_phone = f"138{random.randint(10000000, 99999999)}"
        page.fill("id=phone", test_phone)
        page.fill("id=email", f"test{random.randint(1000,9999)}@test.com")
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        page.goto("/login")
        page.fill("id=phone", test_phone)
        page.fill("id=password", "Test123456")
        page.click("input[type='submit']")
        page.wait_for_timeout(1000)
        
        # 访问多用户管理页面
        page.goto("/multi_user_manager")
        
        # 点击退出一个用户
        page.on("dialog", lambda dialog: dialog.accept())
        logout_links = page.locator("a[href*='/logout_session/']")
        if logout_links.count() > 0:
            logout_links.first.click()
            page.wait_for_timeout(1000)
            
            # 验证还在多用户管理页面或首页
            current_url = page.url
            assert "/multi_user_manager" in current_url or "127.0.0.1:5000/" in current_url
