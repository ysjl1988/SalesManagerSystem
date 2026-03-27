"""
浏览器隔离UI测试
使用 Playwright 测试不同浏览器上下文之间的隔离性
"""
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def browser():
    """创建浏览器实例"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def test_browser_isolation_login(browser):
    """
    测试浏览器隔离：两个独立的浏览器上下文
    验证浏览器A登录admin，浏览器B登录user，互不影响
    """
    import random
    
    # 创建两个独立的浏览器上下文（模拟两个不同的浏览器）
    context_a = browser.new_context()  # 浏览器A
    context_b = browser.new_context()  # 浏览器B
    
    try:
        page_a = context_a.new_page()
        page_b = context_b.new_page()
        
        base_url = "http://127.0.0.1:5000"
        
        # ========== 浏览器A：登录admin ==========
        print("[Test] Browser A logging in as admin...")
        page_a.goto(f"{base_url}/login")
        page_a.fill("id=phone", "13564612895")
        page_a.fill("id=password", "Zk123456")
        page_a.click("input[type='submit']")
        page_a.wait_for_timeout(1000)
        
        # 验证浏览器A登录成功（通过检查是否重定向到首页或修改密码页）
        page_a.goto(f"{base_url}/")
        assert page_a.url == f"{base_url}/" or "/force_change_password" in page_a.url, "Browser A should be logged in"
        print("[Test] Browser A logged in: OK")
        
        # ========== 浏览器B：注册并登录新用户 ==========
        print("[Test] Browser B registering new user...")
        test_phone = f"138{random.randint(10000000, 99999999)}"
        
        page_b.goto(f"{base_url}/register")
        page_b.fill("id=phone", test_phone)
        page_b.fill("id=email", f"test{random.randint(1000,9999)}@test.com")
        page_b.fill("id=password", "Test123456")
        page_b.click("input[type='submit']")
        page_b.wait_for_timeout(1000)
        
        # 登录新用户
        page_b.goto(f"{base_url}/login")
        page_b.fill("id=phone", test_phone)
        page_b.fill("id=password", "Test123456")
        page_b.click("input[type='submit']")
        page_b.wait_for_timeout(1000)
        
        # 验证浏览器B登录成功
        page_b.goto(f"{base_url}/")
        assert page_b.url == f"{base_url}/" or "/force_change_password" in page_b.url, "Browser B should be logged in"
        print(f"[Test] Browser B logged in: OK")
        
        # ========== 关键验证：浏览器A应该仍然保持登录 ==========
        print("[Test] Verifying Browser A still logged in...")
        page_a.goto(f"{base_url}/")
        
        # 浏览器A应该仍然保持登录（检查URL，未登录会重定向到/login）
        assert page_a.url == f"{base_url}/", "Browser A should still be logged in"
        print("[Test] Browser A still logged in: OK")
        
        # ========== 关键验证：浏览器B应该保持自己的登录 ==========
        print("[Test] Verifying Browser B still logged in...")
        page_b.goto(f"{base_url}/")
        
        assert page_b.url == f"{base_url}/", "Browser B should still be logged in"
        print("[Test] Browser B still logged in: OK")
        
        print("[Test] Browser isolation test PASSED!")
        
    finally:
        context_a.close()
        context_b.close()


def test_browser_isolation_after_logout(browser):
    """
    测试浏览器隔离：浏览器B退出不影响浏览器A
    """
    # 创建两个独立的浏览器上下文
    context_a = browser.new_context()
    context_b = browser.new_context()
    
    try:
        page_a = context_a.new_page()
        page_b = context_b.new_page()
        
        base_url = "http://127.0.0.1:5000"
        
        # 浏览器A登录admin
        page_a.goto(f"{base_url}/login")
        page_a.fill("id=phone", "13564612895")
        page_a.fill("id=password", "Zk123456")
        page_a.click("input[type='submit']")
        page_a.wait_for_timeout(1000)
        
        # 浏览器B登录admin（同一账号）
        page_b.goto(f"{base_url}/login")
        page_b.fill("id=phone", "13564612895")
        page_b.fill("id=password", "Zk123456")
        page_b.click("input[type='submit']")
        page_b.wait_for_timeout(1000)
        
        # 浏览器B退出
        page_b.goto(f"{base_url}/logout")
        page_b.wait_for_timeout(1000)
        
        # 验证浏览器A仍然是登录状态（检查URL，未登录会重定向到/login）
        page_a.goto(f"{base_url}/")
        assert page_a.url == f"{base_url}/", "Browser A should still be logged in after Browser B logout"
        
        print("[Test] Browser isolation after logout test PASSED!")
        
    finally:
        context_a.close()
        context_b.close()


if __name__ == "__main__":
    # 直接运行测试
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 设置为False可以看到浏览器
        try:
            test_browser_isolation_login(browser)
            test_browser_isolation_after_logout(browser)
        finally:
            browser.close()
