#!/usr/bin/env python3
"""Telegram Notify — small wrapper that sends a message to your Telegram bot.

Two modes:
  1. No CLI arg → sends a connectivity test ("✅ 텔레그램 연결 정상").
  2. With CLI arg(s) → sends those as the message body. Other tools can call
     this script to push their summaries.

Reads TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID from youtube_account.json."""
import os, json, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ACCOUNT = os.path.join(HERE, "youtube_account.json")

def main():
    if not os.path.exists(ACCOUNT):
        print("❌ youtube_account.json이 없어요.")
        sys.exit(1)
    with open(ACCOUNT, "r", encoding="utf-8") as f:
        acct = json.load(f)
    token = (acct.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat  = (acct.get("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat:
        print("❌ TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 비어있어요.")
        print("   봇 만들기: Telegram에서 @BotFather → /newbot")
        print("   chat_id 찾기: 봇한테 메시지 한 번 보내고")
        print("                  https://api.telegram.org/bot<TOKEN>/getUpdates 열기")
        sys.exit(1)

    if len(sys.argv) > 1:
        body = " ".join(sys.argv[1:])
    else:
        body = f"✅ 텔레그램 연결 정상 — {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n이 메시지가 보이면 다른 YouTube 도구들도 자동으로 보고를 보낼 수 있어요."

    try:
        import requests
    except ImportError:
        print("❌ pip install requests")
        sys.exit(1)
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": body, "parse_mode": "Markdown"},
            timeout=15,
        )
        r.raise_for_status()
        print(f"✅ 전송 OK ({len(body)}자)")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")
        if "Bad Request" in str(e):
            print("   chat_id가 정확한지, 봇과 한 번이라도 대화를 시작했는지 확인하세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()
