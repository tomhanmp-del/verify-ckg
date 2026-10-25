# ============================================================
#  made by drakereborned  ||  Verificacion OAuth2 (Vercel serverless)
#  Gratis, sin tarjeta, HTTPS, no se duerme.
#  Env vars (en Vercel: Project Settings > Environment Variables):
#    DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_BOT_TOKEN,
#    DISCORD_GUILD_ID, DISCORD_REDIRECT_URI, VERIFIED_ROLE_NAME
# ============================================================
import os
import requests
from flask import Flask, request

app = Flask(__name__)

CLIENT_ID     = os.environ.get("DISCORD_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
BOT_TOKEN     = os.environ.get("DISCORD_BOT_TOKEN", "")
GUILD_ID      = os.environ.get("DISCORD_GUILD_ID", "")
REDIRECT_URI  = os.environ.get("DISCORD_REDIRECT_URI", "")
VERIFIED_ROLE = os.environ.get("VERIFIED_ROLE_NAME", "✅ Verificado")

API = "https://discord.com/api/v10"
PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="background:#0a0a14;color:#fff;font-family:system-ui,sans-serif;text-align:center;padding-top:14%">
<h1 style="font-size:42px">🥔 CKG's Community</h1>{body}</body></html>"""


def rol_verificado_id():
    r = requests.get(f"{API}/guilds/{GUILD_ID}/roles",
                     headers={"Authorization": f"Bot {BOT_TOKEN}"}, timeout=15)
    for role in r.json():
        if role["name"] == VERIFIED_ROLE:
            return role["id"]
    return None


@app.route("/")
def home():
    url = (f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}"
           f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify")
    body = (f'<h2>🔒 Verificación</h2>'
            f'<p style="opacity:.8">Autorizá la app para entrar al server.</p>'
            f'<a href="{url}" style="display:inline-block;margin-top:20px;background:#00e5ff;'
            f'color:#000;padding:16px 46px;border-radius:12px;text-decoration:none;'
            f'font-weight:800;font-size:22px">✅ Verificarme</a>')
    return PAGE.format(body=body)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return PAGE.format(body="<h2>❌ Faltó el código. Volvé a intentar.</h2>"), 400

    tok = requests.post(f"{API}/oauth2/token", data={
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI,
    }, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=15).json()

    access = tok.get("access_token")
    if not access:
        return PAGE.format(body="<h2>❌ No se pudo autorizar.</h2>"), 400

    user = requests.get(f"{API}/users/@me",
                        headers={"Authorization": f"Bearer {access}"}, timeout=15).json()
    uid = user.get("id")
    rid = rol_verificado_id()
    if not uid or not rid:
        return PAGE.format(body="<h2>❌ Error interno (rol o usuario).</h2>"), 500

    r = requests.put(f"{API}/guilds/{GUILD_ID}/members/{uid}/roles/{rid}",
                     headers={"Authorization": f"Bot {BOT_TOKEN}"}, timeout=15)
    if r.status_code in (201, 204):
        return PAGE.format(body="<h2>✅ ¡Verificado!</h2>"
                                "<p>Ya podés volver a Discord y ver el server. 🥔</p>")
    return PAGE.format(body=f"<h2>❌ No pude darte el rol ({r.status_code}).</h2>"), 500
