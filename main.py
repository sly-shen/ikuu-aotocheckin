import requests
import os
import pyotp
import time

# 从环境变量获取数据
EMAIL = os.environ.get('IKUUU_EMAIL')
PASSWORD = os.environ.get('IKUUU_PASSWORD')
SECRET_2FA = os.environ.get('IKUUU_2FA_SECRET')
BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
CHAT_ID = os.environ.get('TG_CHAT_ID')
BASE_URL = "https://ikuuu.org"

def send_notify(msg):
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def run():
    print("🚀 开始执行带 2FA 的自动登录与签到...")
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'{BASE_URL}/auth/login'
    }

    # 1. 生成 6 位动态验证码
    if not SECRET_2FA:
        print("❌ 未配置 2FA 密钥！")
        return
    totp = pyotp.TOTP(SECRET_2FA)
    current_code = totp.now()
    print(f"🔑 已自动生成 6 位动态验证码: {current_code}")

    # 2. 模拟登录（带验证码）
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "email": EMAIL,
        "passwd": PASSWORD,
        "code": current_code  # 提交验证码
    }
    
    try:
        print("⏳ 尝试登录账号...")
        login_res = session.post(login_url, data=login_data, headers=headers, timeout=10).json()
        
        if login_res.get('ret') == 1:
            print("✅ 登录成功！")
        else:
            err_msg = f"❌ 登录失败：{login_res.get('msg')}"
            print(err_msg)
            send_notify(err_msg)
            return

        # 3. 发起签到
        time.sleep(2) # 稍微等2秒，模拟真人操作
        checkin_url = f"{BASE_URL}/user/checkin"
        headers['Referer'] = f'{BASE_URL}/user' 
        
        checkin_res = session.post(checkin_url, headers=headers, timeout=10).json()
        msg = checkin_res.get('msg')
        
        # 4. 发送通知
        log = f"📅 **iKuuu 每日签到**\n\n💬 结果：{msg}"
        print(log)
        send_notify(log)
        
    except Exception as e:
        err = f"❌ 脚本运行出错：{str(e)}"
        print(err)
        send_notify(err)

if __name__ == '__main__':
    run()
