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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)
        
        print("🌐 正在打开登录页面...")
        page.goto("https://ikuuu.org/auth/login")
        page.wait_for_timeout(8000) 
        
        print(f"📄 实际加载的网页标题: {page.title()}")
        print("📝 填写账号和密码...")
        page.fill('input[type="email"]', os.environ.get('IKUUU_EMAIL'))
        page.fill('input[type="password"]', os.environ.get('IKUUU_PASSWORD'))
        
        print("⏳ 尝试点击人机验证...")
        try:
            # 针对各种面板常见的验证码底层 CSS 进行盲点
            captcha_selectors = [
                '#embed-captcha',      # 极验常见 ID
                '.geetest_btn',        # 极验常见 Class
                '#turnstile-wrapper',  # CF 常见 ID
                'div[class*="captcha"]',
                'div[id*="captcha"]'
            ]
            
            clicked = False
            for selector in captcha_selectors:
                if page.locator(selector).count() > 0:
                    print(f"🎯 找到了底层组件 [{selector}]，正在点击...")
                    page.locator(selector).first.click(timeout=3000)
                    page.wait_for_timeout(3000)
                    clicked = True
                    break
                    
            if not clicked:
                # 兜底：再试一次文字
                page.locator(':has-text("点我开始验证")').last.click(timeout=3000)
                page.wait_for_timeout(3000)
                print("🎯 成功通过文字点到了按钮！")
                
        except Exception:
            print("⚠️ 依然未找到验证按钮！启动显影液，提取 DOM 源码：")
            try:
                # 核心探针：直接把包含账号密码框的 form 表单源码打印出来
                form_html = page.locator('form').inner_html()
                print("👇👇👇 表单源码如下 👇👇👇")
                print(form_html[:1000]) # 截取前1000个字符避免日志撑爆
                print("👆👆👆 表单源码结束 👆👆👆")
            except Exception as e:
                print(f"获取源码失败: {e}")
            
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
            
        print("⏳ 等待页面跳转...")
        page.wait_for_timeout(5000) 
        print(f"📄 登录后的网页标题: {page.title()}")
        
        if "login" in page.url:
            print("❌ 还在登录页面，登录失败。")
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
