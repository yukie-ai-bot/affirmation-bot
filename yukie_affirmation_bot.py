
# Yukie専用 LINEアファメーションBot（朝8時・夜21時）
# 必要ライブラリ: flask, requests, openai, apscheduler

from flask import Flask, request, abort
import requests
import openai
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

app = Flask(__name__)

# --- 各種キー（Yukie用に差し替え） ---
CHANNEL_ACCESS_TOKEN = 'ここにLINEのアクセストークンを貼る'
CHANNEL_SECRET = 'ここにチャネルシークレットを貼る'
OPENAI_API_KEY = 'ここにOpenAIのAPIキーを貼る'

openai.api_key = OPENAI_API_KEY

def create_affirmation():
    prompt = "60歳女性に寄り添う、前向きな一言アファメーションを1つください。"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=60
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"エラーが発生しました: {e}"

def push_line_message(text):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
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
