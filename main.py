import os
import pyotp
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def run_ikuuu_auto():
    totp = pyotp.TOTP(os.environ.get('IKUUU_2FA_SECRET'))
    current_code = totp.now()
    print(f"🔑 准备就绪，2FA 动态码: {current_code}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)
        
        print("🌐 正在打开登录页面...")
        page.goto("https://ikuuu.org/auth/login")
        page.wait_for_timeout(8000) # 强行等 8 秒，让 iframe 里的验证码飞一会儿
        
        print("📝 填写账号和密码...")
        page.fill('input[type="email"]', os.environ.get('IKUUU_EMAIL'))
        page.fill('input[type="password"]', os.environ.get('IKUUU_PASSWORD'))
        
        print("🕵️ 启动深度扫描：穿透所有 Iframe 寻找验证码...")
        # 遍历网页里嵌着的所有小窗口 (iframe)
        for i, frame in enumerate(page.frames):
            print(f"➡️ 扫描到 Iframe [{i}]: URL={frame.url[:60]}...")
            try:
                # 尝试在每个 iframe 里找具有验证特征的按钮并点击
                captcha_elements = frame.locator(':has-text("点我"), :has-text("验证"), .geetest_btn, #cf-stage, input[type="checkbox"]')
                if captcha_elements.count() > 0:
                    print(f"🎯 破甲成功！在 Iframe [{i}] 中锁定了验证码，正在射击...")
                    captcha_elements.first.click(timeout=3000)
                    page.wait_for_timeout(3000)
            except Exception:
                pass

        print("⏳ 兜底扫描：在主网页使用底层 CSS 盲点...")
        blind_selectors = ['.geetest_radar_btn', '#embed-captcha', 'div.vaptcha-init-main', '#turnstile-wrapper']
        for sel in blind_selectors:
            try:
                if page.locator(sel).count() > 0:
                    print(f"🎯 击中底层选择器 [{sel}]！")
                    page.locator(sel).first.click(timeout=3000)
                    page.wait_for_timeout(3000)
            except: pass
            
        print("🚀 点击登录按钮...")
        page.locator('button:has-text("登录"), button[type="submit"]').first.click()
        
        try:
            print("🔑 等待 2FA 弹窗...")
            two_fa_input = page.locator('.swal2-input, input[id*="code"], input[name="code"], input[placeholder*="动态"]').first
            two_fa_input.wait_for(state="visible", timeout=5000)
            two_fa_input.fill(current_code)
            page.locator('.swal2-confirm, button:has-text("确定"), button:has-text("确认")').first.click()
        except Exception:
            print("⏩ 无 2FA 弹窗。")
            
        print("⏳ 等待页面跳转判定...")
        page.wait_for_timeout(5000) 
        
        # 严格的成功判定逻辑
        if "login" in page.url:
            print("❌ 致命错误：仍在登录页面，未能跨过验证码！")
            browser.close()
            # 抛出异常，让 GitHub Actions 的任务直接标红（Exit 1）
            raise Exception("登录失败，被验证码拦截。")

        print("✅ 登录成功！寻找签到按钮...")
        try:
            page.locator('a:has-text("签到"), button:has-text("签到"), .btn-checkin').first.click(timeout=5000)
            print("🎉 签到成功！")
        except Exception:
            print("📅 没有找到签到按钮，今日大概率已签到。")
            
        browser.close()

if __name__ == "__main__":
    run_ikuuu_auto()
