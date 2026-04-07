import os
import pyotp
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def run_ikuuu_auto():
    totp = pyotp.TOTP(os.environ.get('IKUUU_2FA_SECRET'))
    current_code = totp.now()
    print(f"🔑 当前生成的 2FA 验证码: {current_code}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            # 伪装得更像真人浏览器
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)
        
        print("🌐 正在打开登录页面...")
        page.goto("https://ikuuu.org/auth/login")
        
        # 【关键改动 1】强行等待 8 秒，让所有的防御盾和 iframe 充分加载
        page.wait_for_timeout(8000) 
        
        # 【探针】打印当前页面到底是什么，用来诊断是否被拦截
        print(f"📄 实际加载的网页标题: {page.title()}")
        print(f"🔗 实际停留的 URL: {page.url}")

        print("📝 填写账号和密码...")
        page.fill('input[type="email"]', os.environ.get('IKUUU_EMAIL'))
        page.fill('input[type="password"]', os.environ.get('IKUUU_PASSWORD'))
        
        print("⏳ 尝试点击人机验证...")
        try:
            # 【关键改动 2】尝试穿透所有的 iframe 寻找该按钮
            page.frame_locator("iframe").locator(':has-text("点我开始验证")').first.click(timeout=5000)
            print("🎯 成功在 iframe 中点到了验证按钮！")
            page.wait_for_timeout(3000)
        except Exception:
            try:
                # 备用：在主页面寻找
                page.locator(':has-text("点我开始验证")').last.click(timeout=5000)
                print("🎯 成功在主页面点到了验证按钮！")
                page.wait_for_timeout(3000)
            except Exception:
                print("⚠️ 依然未找到验证按钮！(这说明页面被拦截，或者按钮不是文字)")
            
        print("🚀 点击登录按钮...")
        page.locator('button:has-text("登录"), button[type="submit"]').first.click()
        
        try:
            print("🔑 正在等待 2FA 验证码弹窗...")
            two_fa_input = page.locator('.swal2-input, input[id*="code"], input[name="code"], input[placeholder*="动态"]').first
            two_fa_input.wait_for(state="visible", timeout=5000)
            two_fa_input.fill(current_code)
            page.locator('.swal2-confirm, button:has-text("确定"), button:has-text("确认")').first.click()
            print("✅ 已输入 2FA！")
        except Exception:
            print("⏩ 未检测到 2FA 弹窗。")
            
        # 【探针】检查点击登录后，网页有没有真正发生跳转
        print("⏳ 等待页面跳转...")
        page.wait_for_timeout(5000) # 等待 5 秒看是否跳转
        print(f"📄 登录后的网页标题: {page.title()}")
        print(f"🔗 登录后的 URL: {page.url}")
        
        if "login" in page.url:
            print("❌ 完蛋，还在登录页面，说明登录彻底失败了。")
            browser.close()
            return

        print("🔍 寻找签到按钮...")
        try:
            page.locator('a:has-text("签到"), button:has-text("签到"), .btn-checkin').first.click(timeout=5000)
            print("🎉 签到成功！")
        except Exception:
            print("📅 没有找到签到按钮，可能已签到。")
            
        browser.close()

if __name__ == "__main__":
    run_ikuuu_auto()
