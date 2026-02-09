import requests
import os

# 从 GitHub Secrets 中读取
bot_token = os.environ.get('TG_BOT_TOKEN')
chat_id = os.environ.get('TG_CHAT_ID')

# 这里的逻辑是：利用你自己的 Bot 转发指令给 iKuuu 机器人
# 注意：前提是你已经在 TG 里把你的账号和 iKuuu 机器人绑定了
def telegram_checkin():
    # 发送消息给 iKuuu 机器人的接口 URL
    url = f"https://api.telegram.org/bot{iKuuuu_VPN_bot}/sendMessage"
    
    # 填入 iKuuu 机器人的 ID (例如 @ikuuu_bot)
    data = {
        "chat_id": chat_id,
        "text": "/checkin"
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Webhook 指令发送成功！")
    else:
        print(f"发送失败，错误码：{response.status_code}")

if __name__ == '__main__':
    telegram_checkin()
