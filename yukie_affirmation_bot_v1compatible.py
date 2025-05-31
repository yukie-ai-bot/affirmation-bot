
# Yukie専用 LINEアファメーションBot（朝8時・夜21時）
# 必要ライブラリ: flask, requests, openai, apscheduler

from flask import Flask, request, abort
import requests
import openai
from openai import OpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

app = Flask(__name__)

# --- 各種キー（Yukie用に差し替え） ---
CHANNEL_ACCESS_TOKEN = 'lM85m7qbDpqrF6BUpHs3rXa9TQfUi4RMFquKPHub2QxtbZkZJH4EMp65O1JBzrS27axL+6Ey3so3AZNCd2vVJ+9BVj5JYPT5uteOEjppurGJ7Kn3Muknrm/sQ5bvYxE6M7Xw9hBn7hu4VGbUXmyUCQdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = '84bb8f9b48c8b6635d63a0cd8a555895'
OPENAI_API_KEY = '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'

client = OpenAI(api_key=OPENAI_API_KEY)

def create_affirmation():
    prompt = "60歳女性に寄り添う、前向きな一言アファメーションを1つください。"
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
    push_line_message(f"☀️ おはよう Yukieさん！\n{msg}")

def night_job():
    msg = create_affirmation()
    push_line_message(f"🌙 今日もおつかれさま Yukieさん\n{msg}")

@app.route("/test")
def test():
    push_line_message("📨 これはテスト送信です！（クレセントより）")
    return "テスト送信しました！"

@app.route("/generate")
def generate_now():
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
