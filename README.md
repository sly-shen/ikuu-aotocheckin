# 🚀 iKuuu Auto Checkin (带 2FA 全自动签到)

这是一个基于 GitHub Actions 的 Python 自动化脚本，用于实现 iKuuu 网站的每日自动签到，并通过 Telegram 机器人实时推送运行结果。

## ✨ 核心特性

- **告别 Cookie 过期**：采用账号密码动态模拟登录获取最新 Session，彻底解决静态 Cookie 只能存活 3 天的痛点。
- **完美突破 2FA (二次验证)**：内置 `pyotp` 算法，利用密钥种子自动计算并提交 6 位动态密码，完美复刻真人登录链路。
- **零成本托管**：依托 GitHub Actions 免费服务器，每天定时自动唤醒运行，无需购买云主机或保持电脑开机。
- **消息直达**：利用 Webhook 直连 Telegram Bot API，免受代理和 API ID 申请限制，签到结果第一时间推送到手机。

---

## 🛠️ 部署前准备

在开始配置 GitHub 之前，你需要集齐以下 **5 个关键数据**：

1. **iKuuu 账号**：你的登录邮箱。
2. **iKuuu 密码**：你的登录密码。
3. **2FA 文本密钥**：在 iKuuu 绑定二次验证时，用微信“扫一扫”识别二维码，提取 `otpauth://` 链接中 `secret=` 后面的大写字母与数字组合（例如 `JBSWY3DPEHPK3PXP`）。
4. **TG Bot Token**：在 Telegram 中找 `@BotFather` 创建机器人获取的 Token。
5. **TG Chat ID**：在 Telegram 中找 `@userinfobot` 获取的个人纯数字 ID。（注意：获取后必须去私聊你自己的机器人发一句 `Start` 激活对话）。

---

## 🚀 部署步骤

1. **创建私有仓库**：新建一个 **Private** 仓库，并将本项目的 `main.py` 和 `.github/workflows/run.yml` 上传。
2. **配置环境变量**：
   进入仓库的 **Settings** -> **Secrets and variables** -> **Actions**，点击 **New repository secret**，依次添加以下 5 个变量：
   - `IKUUU_EMAIL`
   - `IKUUU_PASSWORD`
   - `IKUUU_2FA_SECRET`
   - `TG_BOT_TOKEN`
   - `TG_CHAT_ID`
3. **首次测试**：
   进入仓库的 **Actions** 页面，选择左侧的 `Daily Checkin`，点击右侧的 **Run workflow** 手动触发一次运行。如果手机收到 Telegram 通知，即代表部署成功！

---

## ⏰ 定时任务说明

本脚本默认由 GitHub Actions 的 `schedule` 触发。
当前配置的 Cron 表达式为：`17 22 * * *`
- 对应时间：**UTC 22:17** (即 **北京时间早上 6:17**)
- **为什么不是整点？** 避开 GitHub 全球服务器在 `00` 或 `30` 这种整点半点的高峰期大塞车，确保脚本能准时运行。如需修改，请编辑 `.yml` 文件。

---

## ⚠️ 隐私与安全

- **务必保持仓库私有 (Private)**，切勿将 Secrets 泄露给他人。
- 本项目利用纯自动化手段替代人工重复劳动，仅供学习 Python 爬虫、API 对接与 GitHub Actions 工作流使用。
