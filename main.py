import requests
import os

# ================= 变量配置 =================
# 所有的敏感数据都从 GitHub Secrets 读取
COOKIE = os.environ.get('IKUUU_COOKIE')
BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
CHAT_ID = os.environ.get('TG_CHAT_ID')

# iKuuu 官网地址，如果以后变了改这里
BASE_URL = "https://ikuuu.org"
# ===========================================

def send_telegram_notify(message):
    """
    使用 Bot API 发送通知给用户
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 未配置 Telegram 机器人参数，跳过通知")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("✅ Telegram 通知发送成功")
        else:
            print(f"❌ 通知发送失败: {res.text}")
    except Exception as e:
        print(f"❌ 通知网络错误: {e}")

def run_checkin():
    """
    执行网页签到逻辑
    """
    print("🚀 开始执行 iKuuu 签到...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'{BASE_URL}/user',
        'Cookie': COOKIE
    }
    
    checkin_url = f"{BASE_URL}/user/checkin"

    try:
        # 模拟点击签到按钮
        response = requests.post(checkin_url, headers=headers)
        data = response.json()
        
        # 获取返回结果
        msg = data.get('msg')
        ret_code = data.get('ret') # 1 代表成功，0 或其他代表失败或已签到
        
        # 组装通知内容
        log_content = f"📅 **iKuuu 每日签到报告**\n\n💬 结果：{msg}\n🔢 代码：{ret_code}"
        
        print(log_content)
        # 发送通知
        send_telegram_notify(log_content)

    except Exception as e:
        error_msg = f"❌ 脚本执行出错: {str(e)}\n可能是 Cookie 失效或域名无法访问。"
        print(error_msg)
        send_telegram_notify(error_msg)

if __name__ == '__main__':
    run_checkin()
