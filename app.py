import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")  # Es: vspice72-ero/EtnaMonitor
WORKFLOW_FILE = "run_monitor.yml"

# Inserisci qui il tuo ID Telegram numerico (e quello di eventuali amici autorizzati)
AUTORIZZATI_IDS = [430261719,5699356143]  # <-- Sostituisci con il tuo ID reale

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    
    if data and "callback_query" in data:
        callback = data["callback_query"]
        callback_id = callback["id"]
        callback_data = callback.get("data")
        user_id = callback["from"]["id"]  # ID Telegram di chi preme il bottone
        
        if callback_data == "forza_aggiornamento":
            # Controllo di sicurezza: se l'utente non è nella lista, blocca l'azione
            if user_id not in AUTORIZZATI_IDS:
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery",
                    json={
                        "callback_query_id": callback_id,
                        "text": "⛔ Non sei autorizzato ad aggiornare i dati.",
                        "show_alert": True
                    }
                )
                return "OK", 200
            
            # Se l'utente è autorizzato, procede con il normale flusso
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery",
                json={
                    "callback_query_id": callback_id,
                    "text": "⏳ Avvio aggiornamento dati Etna in corso..."
                }
            )
            
            # Invia il comando di avvio a GitHub Actions
            gh_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            payload = {"ref": "main"}
            requests.post(gh_url, headers=headers, json=payload)
            
    return "OK", 200

@app.route('/', methods=['GET'])
def health_check():
    return "EtnaMonitor Webhook is running!", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
