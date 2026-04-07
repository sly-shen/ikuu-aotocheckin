import os
import pyotp
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync  # 保持 1.0.6 版本的导入

def run_ikuuu_auto():
    # 提取并生成 2FA
    totp = pyotp.TOTP(os.environ.get('IKUUU_2FA_SECRET'))
    current_code = totp.now()
    print(f"🔑 当前生成的 2FA 验证码: {current_code}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        stealth_sync(page) # 隐藏机器特征
        
        print("🌐 正在打开登录页面...")
        page.goto("https://ikuuu.org/auth/login")
        
        # 1. 填入账号密码 (截图中可见的元素)
        print("📝 填写账号和密码...")
        page.fill('input[type="email"]', os.environ.get('IKUUU_EMAIL'))
        page.fill('input[type="password"]', os.environ.get('IKUUU_PASSWORD'))
        
        # 2. 点击人机验证按钮
        print("⏳ 尝试点击人机验证...")
        try:
            # 模糊匹配截图中的按钮文字
            page.locator(':has-text("点我开始验证")').last.click(timeout=5000)
            page.wait_for_timeout(3000) # 等待 3 秒让验证通过
            print("👆 验证按钮已点击！")
        except Exception:
            print("⚠️ 未找到验证按钮，可能已自动通过...")
            
        # 3. 点击蓝色的“登录”按钮
        print("🚀 点击登录按钮...")
        page.locator('button:has-text("登录"), button[type="submit"]').first.click()
        
        # 4. 核心修复：处理 2FA 弹窗！
        try:
            print("🔑 正在等待 2FA 验证码弹窗...")
            # 面板通常使用 SweetAlert 弹窗，这里等待输入框出现（最多等 5 秒）
            two_fa_input = page.locator('.swal2-input, input[id*="code"], input[name="code"], input[placeholder*="动态"]').first
            two_fa_input.wait_for(state="visible", timeout=5000)
            
            # 填入验证码
            two_fa_input.fill(current_code)
            print("✅ 已输入 6 位 2FA 动态码！")
            
            # 点击弹窗上的确认/OK按钮
            page.locator('.swal2-confirm, button:has-text("确定"), button:has-text("确认")').first.click()
        except Exception:
            print("⏩ 未检测到 2FA 弹窗（可能未触发），跳过...")
            
        # 5. 等待页面跳转到主页
        print("⏳ 等待页面跳转...")
        page.wait_for_load_state("networkidle", timeout=15000)
        
        # 6. 执行签到
        print("🔍 寻找签到按钮...")
        try:
            # 根据面板常见布局，点击签到按钮
            page.locator('a:has-text("签到"), button:has-text("签到"), .btn-checkin').first.click(timeout=5000)
            print("🎉 签到成功！")
        except Exception:
            print("📅 没有找到签到按钮，可能今天已经签到过了，或者布局有变。")
            
        browser.close()

if __name__ == "__main__":
    run_ikuuu_auto()
