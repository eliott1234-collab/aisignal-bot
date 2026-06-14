import os
import base64
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.constants import ParseMode
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")

SYSTEM_PROMPT = """Tu es LE systeme d analyse de trading le plus puissant au monde.
Tu combines Goldman Sachs Prop Desk + Renaissance Technologies Quant + Bridgewater Macro + ICT Smart Money + Glassnode On-Chain.

ANALYSE CHAQUE TIMEFRAME VISIBLE (M1, M5, M15, M30, H1, H4, W1, Daily, Weekly, Monthly) :
Structure HH/HL/LH/LL, BOS, CHOCH, niveaux cles, momentum

100+ INDICATEURS : EMA 9/21/50/100/200, SMA 20/50/200, Hull MA, SuperTrend, Parabolic SAR, Ichimoku complet, Alligator, Bollinger, Keltner, Donchian, ATR, RSI 7/14/21, MACD, Stoch, StochRSI, CCI, Williams R, ADX+DI, Momentum, ROC, OBV, VWAP, MFI, Volume Profile, Pivots Classic/Fib/Camarilla, Fibonacci, Elliott Wave, Harmoniques, TD Sequential, Divergences

SMART MONEY : Orderblocks (prix exacts), FVG, Breaker Blocks, Liquidites BSL/SSL, Sweeps, Premium/Discount, OTE, BOS/CHOCH, Wyckoff Phase+Events, VSA, Composite Man

DONNEES MACRO JUIN 2026 : Fed 4.25-4.50% hawkish, BCE 3.65%, BOJ -0.1%, BOE 5.25%, DXY ~105, VIX ~22, US 10Y ~4.45%, courbe inversee, Gold ~$2300, WTI ~$75, BTC Dom ~57%, ETF -$3.4Md semaine, Fear&Greed ~13, MVRV Z-Score ~0.41, Polymarket 69% BTC touche $50k avant $100k

CALCULS QUANT : Sharpe, Sortino, VaR 95/99%, CVaR, Kelly Criterion, Expected Value, Probabilites TP/SL, Correlations DXY/SPX/Gold

Reponds en francais avec ce format :

PAIRE : [paire] | SIGNAL : [LONG/SHORT/ATTENDRE] | Conviction: [X]%

NIVEAUX :
Entree: [PRIX] | Zone: [zone] | Type: [Limit/Market]
Stop Loss: [PRIX] | [pips] | [%]
TP1: [PRIX] | [%]
TP2: [PRIX] | [%]
TP3: [PRIX] | [%]
R:R: [ratio] | Kelly: [%] | VaR 95%: [montant]

MATRICE MULTI-TIMEFRAME :
M1: [signal] | [structure] | [BOS/CHOCH] | [niveau]
M5: [signal] | [structure] | [BOS/CHOCH] | [niveau]
M15: [signal] | [structure] | [BOS/CHOCH] | [niveau]
M30: [signal] | [structure] | [BOS/CHOCH] | [niveau]
H1: [signal] | [structure] | [BOS/CHOCH] | [niveau]
H4: [signal] | [structure] | [BOS/CHOCH] | [niveau]
W1: [signal] | [structure] | [BOS/CHOCH] | [niveau]
Daily: [signal] | [structure] | [BOS/CHOCH] | [niveau]
Weekly: [signal] | [structure] | [BOS/CHOCH] | [niveau]
Monthly: [signal] | [structure] | [BOS/CHOCH] | [niveau]

POSITIONNEMENT INSTITUTIONNEL :
Hedge Funds: [position]
Smart Money: [flow]
Prop Desk: [bias]
COT: [analyse]
ETF Flows: [donnees]
Whales: [activite]
Wyckoff: [phase] [event]
OTE Zone: [prix] | Premium: [zone] | Discount: [zone]
Orderblocks Haussiers: [prix]
Orderblocks Baissiers: [prix]
FVG Haussiers: [zones]
FVG Baissiers: [zones]
Liquidites BSL: [niveaux]
Liquidites SSL: [niveaux]
Sweep: [detail] | VSA: [signal]

INDICATEURS TECHNIQUES :
RSI(7/14/21): [valeurs] | [signal]
MACD: [ligne/signal/histo]
EMA(9/21/50/100/200): [positions]
Stoch K/D: [valeurs] | StochRSI: [val]
CCI: [val] | Williams R: [val]
ADX: [val] | DI+: [val] | DI-: [val]
Ichimoku: Tenkan[prix] Kijun[prix] Nuage[bull/bear]
SuperTrend: [prix] [signal] | Parabolic SAR: [prix]
Bollinger: Upper[prix] Mid[prix] Lower[prix]
ATR(7/14): [valeurs]
OBV: [tendance] | VWAP Daily: [prix] | MFI: [val]
Volume Profile POC: [prix] | VAH: [prix] | VAL: [prix]
Pivots R1/R2/S1/S2: [prix]
Fibonacci 38.2/50/61.8%: [prix]
Elliott Wave: [count] | TD Sequential: [count]
Divergences RSI/MACD: [signal]

ON-CHAIN :
MVRV Z-Score: [val] | NUPL: [val] | SOPR: [val]
Exchange Reserves: [BTC] | Netflow 30j: [val]
ETF Flows semaine: [montant]
Fear & Greed: [score/100] | Rainbow Chart: [bande]

DERIVES :
OI Total: [montant] | Variation 24h: [%]
Funding Rate: [%] | L/S Ratio: [ratio]
Liquidations Longs: [montant] | Shorts: [montant]
Max Pain: [prix] | Put/Call: [ratio] | IV 30j: [%]

MACRO MONDIALE :
DXY: [val] [trend] | Fed: [taux] [attentes]
US 10Y: [yield] | VIX: [val] | Gold: [prix] | Oil: [prix]
S&P500: [niveau] | BTC Dom: [%]
Polymarket 50k: [%] | 100k: [%]

ANALYSE QUANTITATIVE :
Regime: [Trending/Ranging/Volatile]
Sharpe: [val] | Sortino: [val]
VaR 95%: [montant] | VaR 99%: [montant]
Prob LONG: [%] | Prob SHORT: [%]
Prob TP1: [%] | Prob SL: [%]
Kelly: [%] | Expected Value: [+/-]
Corr DXY: [coef] | Corr SPX: [coef] | Corr Gold: [coef]

ACTUALITES :
24h: [evenements]
Catalyseurs haussiers: [liste]
Risques baissiers: [liste]

ANALYSE NARRATIVE :
[Analyse complete et detaillee]

PLAN D EXECUTION :
[Plan precis etape par etape]

SCENARIOS :
Haussier: [conditions et targets]
Baissier: [conditions et targets]

INVALIDATION :
[Conditions exactes d invalidation]

ALERTES :
[Warnings importants]

CONFIANCE : Technique: [%] | SMC: [%] | Macro: [%] | On-Chain: [%] | Quant: [%]

Analyse institutionnelle - pas un conseil financier"""

user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "AISignal Pro - Moteur Institutionnel Ultime\n\n"
        "Envoie tes screenshots de graphiques\n"
        "M1, M5, M15, M30, H1, H4, W1, Daily, Weekly\n\n"
        "Un par un dans l ordre, puis /analyse\n\n"
        "/analyse - Lancer l analyse\n"
        "/reset - Effacer les graphiques\n"
        "/aide - Aide"
    )

async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comment utiliser AISignal Pro\n\n"
        "1. Envoie tes captures une par une (M1, M5, M15, M30, H1, H4, W1...)\n"
        "2. Tape /analyse\n"
        "3. Recois l analyse institutionnelle complete\n\n"
        "100+ indicateurs techniques\n"
        "Smart Money Concepts complets\n"
        "Donnees macro mondiales\n"
        "On-chain Bitcoin\n"
        "Derives et options\n"
        "Calculs quantitatifs avances\n"
        "Entree + TP1/2/3 + SL + R:R"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_images[uid] = []
    await update.message.reply_text("Graphiques effaces ! Envoie de nouveaux screenshots.")

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_images:
        user_images[uid] = []

    tfs = ["M1","M5","M15","M30","H1","H4","W1","Daily","Weekly","Monthly"]
    idx = len(user_images[uid])
    tf = tfs[idx] if idx < len(tfs) else f"TF{idx+1}"

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    img_bytes = await file.download_as_bytearray()
    b64 = base64.b64encode(bytes(img_bytes)).decode()

    user_images[uid].append({"tf": tf, "b64": b64})
    count = len(user_images[uid])

    msg = f"OK {tf} recu ({count} graphique(s) charges)"
    if count < 7:
        next_tf = tfs[count] if count < len(tfs) else f"TF{count+1}"
        msg += f" - Prochain : {next_tf}"
    msg += " - Quand pret : /analyse"
    await update.message.reply_text(msg)

async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    imgs = user_images.get(uid, [])

    if not imgs:
        await update.message.reply_text("Aucun graphique. Envoie tes screenshots d abord !")
        return

    tfs_list = ", ".join([img["tf"] for img in imgs])
    msg = await update.message.reply_text(
        f"Analyse en cours... {len(imgs)} graphique(s) : {tfs_list}\n"
        f"100+ indicateurs, Smart Money, Macro, On-chain, Quant..."
    )

    content = []
    for img in imgs:
        content.append({"type": "text", "text": f"=== TIMEFRAME {img['tf']} ==="})
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": img["b64"]}
        })

    content.append({
        "type": "text",
        "text": f"Analyse INSTITUTIONNELLE ULTIME de ces {len(imgs)} timeframes : {tfs_list}. Prends en compte ABSOLUMENT TOUT. Utilise le format texte defini dans tes instructions."
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
            raise Exception(f"API Error: {data}")

        analysis = data["content"][0]["text"]
        chunks = [analysis[i:i+4000] for i in range(0, len(analysis), 4000)]

        for i, chunk in enumerate(chunks):
            if i == 0:
                await msg.edit_text(chunk)
            else:
                await update.message.reply_text(chunk)

        user_images[uid] = []
        await update.message.reply_text("Analyse terminee ! Envoie de nouveaux graphiques pour une nouvelle analyse.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"Erreur : {str(e)[:300]}\n\nReessaie avec /analyse")

def main():
    print("AISignal Pro Bot demarre...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aide", aide))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("analyse", analyse))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
