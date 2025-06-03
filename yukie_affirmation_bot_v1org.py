
# Yukie専用 LINEアファメーションBot（朝8時・夜21時）
# OpenAI API v1+ (sk-proj) + organization対応版
# 必要ライブラリ: flask, requests, openai>=1.0.0, apscheduler

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
import requests
from openai import OpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

app = Flask(__name__)

# --- 各種キー（Yukie用に差し替え） ---
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_ORG_ID = os.getenv('OPENAI_ORG_ID')

client = OpenAI(
    api_key=OPENAI_API_KEY,
    organization=OPENAI_ORG_ID,
    project="proj_I2YGJA5rUDSBEJYswpKw7mH3"
)
def create_affirmation():
    prompt = "新しいことにチャレンジ、絶対AIエンジニアで社会に貢献する、絶対猫のSolaチャンネルが大ヒット、絶対願いが叶う一言アファメーションを1つください。"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=60
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"エラーが発生しました: {e}"

def push_line_message(text):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "messages": [{
            "type": "text",
            "text": text
        }]
    }
    requests.post(url, headers=headers, json=body)

def morning_job():
    msg = create_affirmation()
    if len(msg) > 400:
        msg = msg[:400] + "..."  # 長すぎたらカット
    push_line_message(f"☀️ おはよう Yukieさん！\n{msg}")

def night_job():
    msg = create_affirmation()
    if len(msg) > 400:
        msg = msg[:400] + "..."
    push_line_message(f"🌙 今日もおつかれさま Yukieさん\n{msg}")

@app.route("/test")
def test():
    push_line_message("📨 これはテスト送信です！（クレセントより）")
    return "テスト送信しました！"

@app.route("/generate")
def generate():
    msg = create_affirmation()
    push_line_message(f"🧘 Yukieさんの今夜のアファメ：\n{msg}")
    return "アファメーション送信しました！"

# スケジューラー設定
scheduler = BackgroundScheduler(timezone='Asia/Tokyo')
scheduler.add_job(morning_job, 'cron', hour=8, minute=0)
scheduler.add_job(night_job, 'cron', hour=21, minute=0)
scheduler.start()

@app.route("/")
def index():
    return "Yukie Affirmation Bot is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
