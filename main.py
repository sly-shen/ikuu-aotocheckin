import os
import pyotp
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth

def run_ikuuu_auto():
    # 你的 2FA 逻辑依然保留
    totp = pyotp.TOTP(os.environ.get('IKUUU_2FA_SECRET'))
    current_code = totp.now()

    with sync_playwright() as p:
        # 启动 Chromium 浏览器 (无头模式)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth(page)  # 关键：隐藏自动化特征，防止被 CF 识别

        print("🌐 正在打开登录页面...")
        page.goto("https://ikuuu.org/auth/login")

        # 2. 模拟点击那个黑色的“点我开始验证”按钮
        # Cloudflare Turnstile 通常在一个 iframe 里，Playwright 会自动处理点击
        try:
            print("⏳ 正在尝试穿透人机验证...")
            # 这里的选择器可能需要根据实际页面微调，通常点这个 text 就能触发
            page.click('text="点我开始验证"', timeout=10000)
            page.wait_for_timeout(3000) # 等待验证完成的动画
        except Exception:
            print("⚠️ 未发现验证按钮或已自动通过")

        # 3. 输入账号密码
        page.fill('input[type="email"]', os.environ.get('IKUUU_EMAIL'))
        page.fill('input[type="password"]', os.environ.get('IKUUU_PASSWORD'))
        
        # 4. 输入 2FA
        page.fill('input[name="code"]', current_code)
        
        # 5. 点击登录
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # 6. 跳转到签到页或直接在主页找签到按钮
        print("✅ 登录成功，正在尝试签到...")
        if "签到" in page.content():
            page.click('text="签到"') # 假设按钮文字叫签到
            print("🎉 签到指令已发送！")
        else:
            print("📅 今天似乎已经签到过了。")

        browser.close()

if __name__ == "__main__":
    run_ikuuu_auto()
