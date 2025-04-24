import requests
import feedparser
import smtplib
from email.message import EmailMessage
from datetime import datetime

# --- CONFIGURACIÓN ---
SENDER_EMAIL      = "federico.diaz.2004@gmail.com"
# Guarda en tu sistema: export GMAIL_APP_PASSWORD="tu_app_password"
SENDER_PASSWORD   = "zsgh otnf tpqc zslc"
RECIPIENT_EMAIL   = "fedediaz008@gmail.com"

BLUELYTICS_URL    = "https://api.bluelytics.com.ar/v2/latest"
RSS_URL           = "https://www.clarin.com/rss/economia/"

def fetch_dolar_rates():
    """Obtiene cotizaciones oficial y blue de Bluelytics."""
    resp = requests.get(BLUELYTICS_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data["oficial"], data["blue"]

def fetch_news_headlines(limit=5):
    """Toma los primeros 'limit' titulares del RSS de Economía."""
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:limit]
    headlines = []
    for e in entries:
        if hasattr(e, "published_parsed"):
            pub = datetime(*e.published_parsed[:6]).strftime("%d/%m %H:%M")
        else:
            pub = "–"
        headlines.append(f"- {e.title} ({pub})\n  {e.link}")
    return "\n".join(headlines)

def build_and_send_mail():
    """Construye el mensaje y lo envía vía SMTP."""
    try:
        oficial, blue = fetch_dolar_rates()
        news = fetch_news_headlines()
    except Exception as e:
        print(f"[{datetime.now():%H:%M}] Error al obtener datos: {e}")
        return

    subject = f"Dólar Oficial: ${oficial['value_sell']} | Blue: ${blue['value_sell']}"
    body = f"""
Cotizaciones al {datetime.now():%d/%m/%Y %H:%M}:

• Oficial – Compra: ${oficial['value_buy']} / Venta: ${oficial['value_sell']}
• Blue    – Compra: ${blue['value_buy']} / Venta: ${blue['value_sell']}

Noticias destacadas de Economía:
{news}

Saludos,
Tu bot de cotizaciones
"""

    msg = EmailMessage()
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.set_content(body)

    # Envío seguro con SSL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

    print(f"[{datetime.now():%H:%M}] Correo enviado.")

if __name__ == "__main__":
    # Llamada directa al envío de correo al ejecutar el script
    print("Enviando correo...")
    build_and_send_mail()
