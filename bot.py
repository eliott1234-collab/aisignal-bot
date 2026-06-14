import os
import base64
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")

SYSTEM_PROMPT = """Tu es LE systeme d analyse de trading le plus puissant au monde.
Tu combines Goldman Sachs + Renaissance Technologies + Bridgewater + ICT Smart Money + Glassnode.

ANALYSE CHAQUE TIMEFRAME (M1, M5, M15, M30, H1, H4, W1, Daily, Weekly, Monthly).

100+ INDICATEURS : EMA 9/21/50/100/200, SMA, Hull MA, SuperTrend, Parabolic SAR, Ichimoku complet, Bollinger, Keltner, Donchian, ATR, RSI 7/14/21, MACD, Stoch, StochRSI, CCI, Williams R, ADX+DI, OBV, VWAP, MFI, Volume Profile, Pivots, Fibonacci, Elliott Wave, TD Sequential, Divergences.

SMART MONEY : Orderblocks, FVG, Liquidity BSL/SSL, Sweeps, Premium/Discount, OTE, BOS/CHOCH, Wyckoff, VSA.

MACRO JUIN 2026 : Fed 4.25%, BCE 3.65%, DXY ~105, VIX ~22, US 10Y ~4.45%, BTC Dom ~57%, ETF -3.4Md, Fear&Greed ~13, MVRV ~0.41.

QUANT : Sharpe, Sortino, VaR, Kelly, Probabilites TP/SL, Correlations.

Format de reponse :

PAIRE: [paire] | SIGNAL: LONG/SHORT/ATTENDRE | Conviction: X%

NIVEAUX:
Entree: [prix] | SL: [prix] | TP1: [prix] | TP2: [prix] | TP3: [prix]
R:R: [ratio] | Kelly: [%] | VaR 95%: [montant]

TIMEFRAMES:
M1: [signal] | [structure] | [niveau]
M5: [signal] | [structure] | [niveau]
M15: [signal] | [structure] | [niveau]
M30: [signal] | [structure] | [niveau]
H1: [signal] | [structure] | [niveau]
H4: [signal] | [structure] | [niveau]
W1: [signal] | [structure] | [niveau]
Daily: [signal] | [structure] | [niveau]
Weekly: [signal] | [structure] | [niveau]
Monthly: [signal] | [structure] | [niveau]

INSTITUTIONNEL:
Hedge Funds: [position]
Smart Money: [flow]
Prop Desk: [bias]
COT: [analyse]
ETF Flows: [donnees]
Whales: [activite]
Wyckoff: [phase] [event]
Orderblocks Haussiers: [prix]
Orderblocks Baissiers: [prix]
FVG: [zones]
Liquidites BSL: [niveaux] | SSL: [niveaux]
OTE: [prix] | Premium: [zone] | Discount: [zone]
VSA: [signal]

INDICATEURS:
RSI 7/14/21: [valeurs]
MACD: [ligne/signal/histo]
EMA 9/21/50/100/200: [positions]
Stoch K/D: [valeurs] | StochRSI: [val]
CCI: [val] | Williams R: [val]
ADX: [val] | DI+: [val] | DI-: [val]
Ichimoku: Tenkan[prix] Kijun[prix] Nuage[signal]
SuperTrend: [prix] [signal]
Bollinger: Upper[prix] Mid[prix] Lower[prix]
ATR: [val] | OBV: [tendance] | VWAP: [prix]
MFI: [val] | Volume POC: [prix]
Pivots R1/R2/S1/S2: [prix]
Fibonacci 38.2/50/61.8: [prix]
Elliott Wave: [count] | TD Sequential: [count]
Divergences: [signal]

ON-CHAIN:
MVRV: [val] | NUPL: [val] | SOPR: [val]
Exchange Reserves: [BTC] | Netflow: [val]
ETF Flows: [montant] | Fear&Greed: [score]

DERIVES:
OI: [montant] | Funding: [%] | L/S: [ratio]
Liquidations: Longs[montant] Shorts[montant]
Max Pain: [prix] | Put/Call: [ratio] | IV: [%]

MACRO:
DXY: [val] | Fed: [taux] | US 10Y: [yield]
VIX: [val] | Gold: [prix] | Oil: [prix]
SP500: [niveau] | BTC Dom: [%]
Polymarket 50k: [%] | 100k: [%]

QUANT:
Regime: [Trending/Ranging/Volatile]
Sharpe: [val] | Sortino: [val]
VaR 95%: [montant] | VaR 99%: [montant]
Prob LONG: [%] | Prob SHORT: [%]
Prob TP1: [%] | Prob SL: [%]
Kelly: [%] | EV: [+/-]
Corr DXY: [coef] | Corr SPX: [coef]

ACTUALITES:
24h: [evenements]
Catalyseurs haussiers: [liste]
Risques baissiers: [liste]

ANALYSE:
[Analyse narrative complete]

EXECUTION:
[Plan d execution precis]

SCENARIOS:
Haussier: [conditions]
Baissier: [conditions]

INVALIDATION:
[Conditions exactes]

ALERTES:
[Warnings]

CONFIANCE: Technique:[%] SMC:[%] Macro:[%] OnChain:[%] Quant:[%]

Pas un conseil financier."""

user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "AISignal Pro - Moteur Institutionnel Ultime\n\n"
        "Envoie tes screenshots de graphiques un par un\n"
        "M1, M5, M15, M30, H1, H4, W1, Daily, Weekly\n\n"
        "Puis tape /analyse\n\n"
        "Commandes:\n"
        "/analyse - Lancer l analyse\n"
        "/reset - Effacer les graphiques\n"
        "/aide - Aide"
    )

async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Mode d emploi:\n\n"
        "1. Envoie tes captures une par une (M1, M5, M15...)\n"
        "2. Tape /analyse\n"
        "3. Recois l analyse complete\n\n"
        "Ce que tu recois:\n"
        "- 100+ indicateurs techniques\n"
        "- Smart Money Concepts\n"
        "- Macro mondiale\n"
        "- On-chain Bitcoin\n"
        "- Derives et options\n"
        "- Calculs quantitatifs\n"
        "- Entree + TP1/2/3 + SL + R:R"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_images[uid] = []
    await update.message.reply_text("Graphiques effaces. Envoie de nouveaux screenshots.")

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_images:
        user_images[uid] = []

    tfs = ["M1","M5","M15","M30","H1","H4","W1","Daily","Weekly","Monthly"]
    idx = len(user_images[uid])
    tf = tfs[idx] if idx < len(tfs) else "TF" + str(idx+1)

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    img_bytes = await file.download_as_bytearray()
    b64 = base64.b64encode(bytes(img_bytes)).decode()

    user_images[uid].append({"tf": tf, "b64": b64})
    count = len(user_images[uid])

    reply = str(count) + " graphique(s) charge(s) - " + tf + " OK"
    if count < 7:
        next_tf = tfs[count] if count < len(tfs) else "TF" + str(count+1)
        reply += " - Prochain: " + next_tf
    reply += " - Tape /analyse quand pret"
    await update.message.reply_text(reply)

async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    imgs = user_images.get(uid, [])

    if not imgs:
        await update.message.reply_text("Aucun graphique charge. Envoie tes screenshots d abord.")
        return

    tfs_list = ", ".join([img["tf"] for img in imgs])
    msg = await update.message.reply_text(
        "Analyse en cours... " + str(len(imgs)) + " graphique(s): " + tfs_list + "\n"
        "100+ indicateurs, Smart Money, Macro, On-chain, Quant en cours..."
    )

    content = []
    for img in imgs:
        content.append({"type": "text", "text": "=== TIMEFRAME " + img["tf"] + " ==="})
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": img["b64"]}
        })

    content.append({
        "type": "text",
        "text": "Analyse INSTITUTIONNELLE ULTIME de ces " + str(len(imgs)) + " timeframes: " + tfs_list + ". Prends en compte ABSOLUMENT TOUT. Utilise le format texte defini."
    })

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 4000,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": content}]
                }
            )

        data = resp.json()
        if "content" not in data:
            raise Exception("API Error: " + str(data))

        analysis = data["content"][0]["text"]
        chunks = [analysis[i:i+4000] for i in range(0, len(analysis), 4000)]

        for i, chunk in enumerate(chunks):
            if i == 0:
                await msg.edit_text(chunk)
            else:
                await update.message.reply_text(chunk)

        user_images[uid] = []
        await update.message.reply_text("Analyse terminee. Envoie de nouveaux graphiques pour recommencer.")

    except Exception as e:
        logger.error("Error: " + str(e))
        try:
            await msg.edit_text("Erreur: " + str(e)[:300] + "\n\nReessaie avec /analyse")
        except Exception:
            await update.message.reply_text("Erreur. Reessaie avec /analyse")

if __name__ == "__main__":
    print("AISignal Pro Bot demarre...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aide", aide))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("analyse", analyse))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    app.run_polling(allowed_updates=Update.ALL_TYPES)
