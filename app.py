import os
import requests
from flask import Flask, request

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")  # Esempio: "tuo-username/nome-repo"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if "callback_query" in data:
        callback = data["callback_query"]
        callback_data = callback.get("data")
        chat_id = callback["message"]["chat"]["id"]
        callback_id = callback["id"]

        if callback_data == "forza_aggiornamento":
            # 1. Rimuove l'animazione di caricamento dal bottone su Telegram
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery", json={
                "callback_query_id": callback_id,
                "text": "🚀 Avvio aggiornamento richiesto..."
            })

            # 2. Chiama l'API di GitHub per fare partire il workflow
            gh_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/monitor.yml/dispatches"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json"
            }
            requests.post(gh_url, json={"ref": "main"}, headers=headers)

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
