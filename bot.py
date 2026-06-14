import os
import base64
import json
import httpx
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.constants import ParseMode

# ═══════════════════════════════════════════════
# ⚠️ REMPLACE CES 2 VALEURS
TELEGRAM_TOKEN = "TON_TELEGRAM_BOT_TOKEN"   # BotFather → /newbot
ANTHROPIC_KEY  = "TON_ANTHROPIC_API_KEY"    # console.anthropic.com
# ═══════════════════════════════════════════════

SYSTEM_PROMPT = """Tu es LE système d'analyse de trading le plus puissant et exhaustif qui existe au monde.
Tu combines : Goldman Sachs Prop Desk + Renaissance Technologies Quant + Bridgewater Macro + ICT Smart Money + Glassnode On-Chain.

═══ ANALYSE CHAQUE TIMEFRAME (M1→Monthly) ═══
Pour chaque TF visible : structure HH/HL/LH/LL, BOS, CHOCH, niveaux clés exacts, momentum, confluences

═══ 100+ INDICATEURS TECHNIQUES ═══
TENDANCE: EMA 9/21/50/100/200, SMA 20/50/200, Hull MA, DEMA, TEMA, VWMA, SuperTrend, Parabolic SAR, Ichimoku complet (Tenkan/Kijun/Senkou A&B/Chikou), Alligator, Donchian, Keltner, Linear Regression
MOMENTUM: RSI 7/14/21, MACD 12/26/9, Stoch 14/3/3, StochRSI, CCI, Williams %R, Momentum, ROC, Awesome Osc, Accelerator Osc, DeMarker, Bears/Bulls Power, Elder Ray, Elder Impulse, Coppock, DPO, Aroon, TRIX, Ultimate Osc, ADX+DI+/DI-
VOLUME: OBV, VWAP daily/weekly, Volume Profile POC/VAH/VAL, MFI, Chaikin MF, Force Index, A/D Line
VOLATILITÉ: Bollinger 20/2σ+3σ, ATR 7/14, Historical Vol, Chaikin Vol, Mass Index
PIVOTS: Classic R1-R3/S1-S3, Fibonacci, Camarilla, Woodie, DeMark
AVANCÉS: Heikin Ashi, Elliott Wave, Harmoniques (Gartley/Bat/Butterfly/Crab), Divergences cachées RSI/MACD/OBV, TD Sequential, Gann angles, Fibonacci 23.6/38.2/50/61.8/78.6/127.2/161.8

═══ SMART MONEY CONCEPTS COMPLETS ═══
Orderblocks haussiers/baissiers (prix exacts), Fair Value Gaps bull/bear, Breaker Blocks, Mitigation Blocks, Liquidity Pools buy-side/sell-side, Stop Hunts/Sweeps, Premium/Discount zones, OTE (62-79% Fibo), BOS/CHOCH, Wyckoff Phase A/B/C/D/E + events (PS/SC/AR/ST/Spring/SOS/LPS/SOW/UTAD/LPSY), Volume Spread Analysis, Composite Man footprint

═══ DONNÉES MACRO MONDIALES RÉELLES (JUIN 2026) ═══
Fed 4.25-4.50% hawkish, BCE 3.65%, BOJ -0.1%, BOE 5.25%
US: CPI 3.1%, Core PCE 2.8%, NFP solide, GDP ralenti
DXY ~105 (fort→bearish crypto), VIX ~22, Gold ~$2300, WTI ~$75, Copper faible
US 10Y ~4.45%, courbe inversée, spreads HY s'écartent
S&P500 fragile, Nasdaq tenu par IA, Russell2000 faible
BTC Dominance ~56-59%, Total ~$2.28T, ETH/BTC faible, Stablecoin supply proche ATH
Géopolitique: tensions US-Chine, Ukraine, Moyen-Orient

═══ ON-CHAIN BITCOIN RÉELS (JUIN 2026) ═══
MVRV Z-Score ~0.41 (fair value), NUPL ~0.28, Realized Price ~$51k
SOPR < 1 (pertes réalisées), LTH-SOPR fort, STH-SOPR faible
Exchange Reserves ~2.69M BTC (-170k en 6 mois = bullish LT), Netflow +114k BTC 30j (bearish CT)
ETF flows: -$3.4Md semaine record (IBIT -448M$, FBTC -63M$) = BEARISH MAJEUR
Hash Rate stable, LTH Supply >70%, S2F sous modèle, Rainbow Chart "Fire Sale", Puell Multiple faible

═══ DÉRIVÉS RÉELS ═══
OI total ~$25Md en baisse, Funding ~0.0005% neutre, Liq longs > shorts
Fear&Greed ~12-13 (Extreme Fear), Max Pain ~$60-62k, Put/Call élevé, IV skew baissier
Polymarket: 69% BTC touche $50k avant $100k, 64% BTC sous $55k fin 2026

═══ CALCULS MATH AVANCÉS ═══
Vol historique, Sharpe, Sortino, Calmar, VaR 95%/99%, CVaR, Expected Move
Probabilités TP1/TP2/TP3/SL, Kelly Criterion, Expected Value
Corrélations DXY/SPX/Gold/ETH/VIX, Z-score, Skewness/Kurtosis
Régimes: Trending/Ranging/Volatile, momentum composite, mean-reversion score

═══ FORMAT DE RÉPONSE ═══
Réponds en français avec ce format EXACT et complet :

🎯 *PAIRE* | *SIGNAL* | Conviction: X%

━━━ 📊 NIVEAUX D'EXÉCUTION ━━━
📍 Entrée: [PRIX] ([zone] · [type: Limit/Market/Stop])
🛑 Stop Loss: [PRIX] ([pips] · [%] du capital)
🎯 TP1: [PRIX] ([%])
🎯 TP2: [PRIX] ([%])
🎯 TP3: [PRIX] ([%])
⚖️ R:R: [ratio] | Kelly: [%] | VaR 95%: [montant] | Move 24h: [%]

━━━ 📈 MATRICE MULTI-TIMEFRAME ━━━
M1: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]
M5: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]
M15: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]
M30: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]
H1: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]
H4: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]
W1: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]
Daily: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]
Weekly: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]
Monthly: [signal] | [structure] | [BOS/CHOCH] | [niveau clé]

━━━ 🏦 POSITIONNEMENT INSTITUTIONNEL ━━━
Hedge Funds: [position exacte]
Smart Money: [flow direction]
Prop Desk: [bias]
COT Report: [commerciaux vs non-commerciaux]
ETF Flows: [données réelles]
Whales: [activité]
Wyckoff: [phase] · [event]
Structure: [BOS/CHOCH global]
OTE Zone: [prix]
Premium: [zone] | Discount: [zone]
Orderblocks 🟢: [prix exacts]
Orderblocks 🔴: [prix exacts]
FVG 🟢: [zones]
FVG 🔴: [zones]
Liquidités BSL: [niveaux]
Liquidités SSL: [niveaux]
Liquidity Sweep: [détail]
VSA: [signal]
Composite Man: [footprint]

━━━ 📉 100+ INDICATEURS TECHNIQUES ━━━
RSI(7/14/21): [valeurs] | [signal]
MACD(12/26/9): [ligne/signal/histo] | [signal]
EMA(9/21/50/100/200): [positions prix]
SMA(20/50/200): [positions prix]
Hull MA / DEMA / TEMA: [signal]
Stoch(14,3,3): [K/D] | StochRSI: [valeur]
CCI: [valeur] | Williams %R: [valeur]
ADX: [valeur] | DI+: [valeur] | DI-: [valeur]
Momentum / ROC(10/20): [valeurs]
Awesome Osc / Accelerator: [signal]
Bears/Bulls Power / Elder Ray: [signal]
Aroon(up/down) / TRIX / DPO: [signal]
Ultimate Osc / Coppock: [signal]
Ichimoku: Tenkan [prix] / Kijun [prix] / Nuage [bull/bear] / Chikou [signal]
SuperTrend: [prix] [direction]
Parabolic SAR: [prix] [signal]
Alligator: [signal]
Bollinger(20,2σ): Upper [prix] / Mid [prix] / Lower [prix] / Squeeze [oui/non]
Bollinger(20,3σ): Upper [prix] / Lower [prix]
Keltner: Upper [prix] / Lower [prix]
Donchian: Upper [prix] / Lower [prix]
ATR(7/14): [valeurs]
Volatilité historique(20/30): [%]
OBV: [tendance]
VWAP Daily: [prix] | VWAP Weekly: [prix]
MFI: [valeur] | Chaikin MF: [signal]
Force Index / A/D Line: [signal]
Volume Profile: POC [prix] / VAH [prix] / VAL [prix]
Pivots Classic: R1[prix] R2[prix] R3[prix] / S1[prix] S2[prix] S3[prix]
Pivots Fibonacci: R1[prix] / S1[prix]
Pivots Camarilla: R3[prix] / S3[prix]
Fibonacci Retracements: 23.6%[prix] 38.2%[prix] 50%[prix] 61.8%[prix] 78.6%[prix]
Fibonacci Extensions: 127.2%[prix] 161.8%[prix] 261.8%[prix]
Elliott Wave: [vague actuelle et compte]
Harmoniques: [pattern détecté si applicable]
TD Sequential: [compte actuel]
Divergences: RSI[bull/bear] MACD[bull/bear] OBV[bull/bear]
Heikin Ashi: [signal]
Régression linéaire: [slope/R²]
Gann 1×1: [prix]

━━━ ⛓️ ON-CHAIN BITCOIN ━━━
MVRV Z-Score: [valeur] ([signal])
NUPL: [valeur] ([signal])
SOPR: [valeur] | LTH-SOPR: [valeur] | STH-SOPR: [valeur]
Realized Price: [prix]
Exchange Reserves: [BTC] ([netflow 30j])
ETF Flows: [données semaine]
LTH Supply: [%] | STH Supply: [%]
Miner Outflows: [signal]
Hash Rate: [signal]
Puell Multiple: [valeur]
S2F Deviation: [signal]
Rainbow Chart: [bande]
Reserve Risk: [valeur]
NVT Signal: [valeur]
Stablecoin Supply: [signal]

━━━ 📊 DÉRIVÉS & OPTIONS ━━━
Open Interest Total: [montant] ([variation 24h])
Funding Rate: [%] ([signal])
Long/Short Ratio: [ratio]
Liquidations: Longs [montant] | Shorts [montant]
Options Max Pain: [prix]
Put/Call Ratio: [valeur]
Gamma Exposure: [signal]
IV 30j: [%] | IV Skew: [signal]
Strikes majeurs: [niveaux]

━━━ 🌍 MACRO MONDIALE ━━━
DXY: [valeur] [trend] → Impact BTC: [bullish/bearish]
Fed: [taux] · [attentes prochaine réunion]
BCE: [taux] | BOJ: [taux] | BOE: [taux]
US 10Y: [yield] | 2Y: [yield] | Courbe: [invertée/normale]
VIX: [valeur] [signal]
Gold: [prix] | Oil WTI: [prix] | Copper: [signal]
S&P500: [niveau] [trend] | Nasdaq: [signal]
BTC Dominance: [%] | ETH/BTC: [ratio]
Liquidité globale: [expansion/contraction]
M2 US: [signal]
Risk Sentiment: [risk-on/risk-off]
Géopolitique: [impact]
Fear & Greed: [score/100]
Polymarket 50k: [%] | 100k: [%]

━━━ 📰 ACTUALITÉS & SENTIMENT ━━━
Événements 24h: [liste]
Événements 48h: [liste]
Calendrier semaine: [données importantes]
Régulation: [impact]
Institutionnel: [news]
Sentiment social: [score]
Catalyseurs 🟢: [liste]
Catalyseurs 🔴: [liste]
Risques: [liste]
Black Swan: [risques]

━━━ 🔢 ANALYSE QUANTITATIVE ━━━
Régime volatilité: [Low/Normal/High/Extreme]
Vol réalisée 30j: [%] annualisée
Force tendance: [score/100]
Mean Reversion Score: [signal]
Momentum Composite: [score]
Market Regime: [Trending/Ranging/Volatile]
Corrélation DXY: [coefficient] | SPX: [coefficient] | Gold: [coefficient] | VIX: [coefficient]
Z-Score prix 30j: [valeur σ]
Sharpe estimé: [valeur]
Sortino Ratio: [valeur]
VaR 95%: [montant] | VaR 99%: [montant] | CVaR 95%: [montant]
Expected Move 24h: [%] | 7j: [%]
Prob. LONG: [%] | Prob. SHORT: [%]
Prob. TP1: [%] | Prob. TP2: [%] | Prob. TP3: [%] | Prob. SL: [%]
Kelly Criterion: [%] | Kelly/2: [%]
Expected Value: [+/- $]
Edge statistique: [%]

━━━ 📖 ANALYSE NARRATIVE ━━━
[Analyse complète et détaillée de la situation — minimum 5 phrases — explique tout le contexte technique, institutionnel et macro]

━━━ 🎯 PLAN D'EXÉCUTION ━━━
[Plan d'entrée précis étape par étape]

━━━ 📊 SCÉNARIOS ━━━
🟢 Haussier: [conditions et targets]
🔴 Baissier: [conditions et targets]

━━━ ❌ INVALIDATION ━━━
[Conditions exactes qui invalident le scénario]

━━━ ⚠️ ALERTES ━━━
[Warnings importants]

━━━ 🕐 NOTE DE TIMING ━━━
[Meilleur moment pour entrer]

━━━ 💯 CONFIANCE PAR CATÉGORIE ━━━
Technique: [%] | Smart Money: [%] | Macro: [%] | On-Chain: [%] | Dérivés: [%] | Quant: [%]

⚠️ _Analyse institutionnelle — pas un conseil financier_"""

# Storage pour les images par utilisateur
user_images: dict = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏦 *AISignal Pro — Moteur Institutionnel Ultime*\n\n"
        "Envoie-moi tes screenshots de graphiques 📊\n"
        "*(M1, M5, M15, M30, H1, H4, W1, Daily, Weekly, Monthly)*\n\n"
        "Envoie-les un par un dans l'ordre, puis tape /analyse\n\n"
        "Commandes:\n"
        "/analyse — Lance l'analyse complète\n"
        "/reset — Efface les graphiques\n"
        "/aide — Aide",
        parse_mode=ParseMode.MARKDOWN
    )

async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Comment utiliser AISignal Pro*\n\n"
        "1️⃣ Envoie tes captures de graphiques une par une\n"
        "   _(dans l'ordre: M1 → M5 → M15 → M30 → H1 → H4 → W1 → Daily → Weekly → Monthly)_\n\n"
        "2️⃣ Tape /analyse quand tu as envoyé tous tes graphiques\n\n"
        "3️⃣ Reçois l'analyse institutionnelle complète :\n"
        "   • 100+ indicateurs techniques\n"
        "   • Smart Money Concepts\n"
        "   • Données macro mondiales\n"
        "   • On-chain Bitcoin\n"
        "   • Dérivés et options\n"
        "   • Calculs quantitatifs\n"
        "   • Entrée + TP1/2/3 + SL + R:R\n\n"
        "💡 Tu peux envoyer de 1 à 10 graphiques",
        parse_mode=ParseMode.MARKDOWN
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_images[uid] = []
    await update.message.reply_text("🗑️ Graphiques effacés. Envoie de nouveaux screenshots !")

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_images:
        user_images[uid] = []

    tfs = ["M1","M5","M15","M30","H1","H4","W1","Daily","Weekly","Monthly"]
    idx = len(user_images[uid])
    tf_label = tfs[idx] if idx < len(tfs) else f"TF{idx+1}"

    # Download photo
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    img_bytes = await file.download_as_bytearray()
    b64 = base64.b64encode(img_bytes).decode()

    user_images[uid].append({"tf": tf_label, "b64": b64})

    count = len(user_images[uid])
    remaining = max(0, 7 - count)
    msg = f"✅ *{tf_label}* reçu ({count} graphique{'s' if count>1 else ''})"
    if remaining > 0:
        next_tf = tfs[count] if count < len(tfs) else f"TF{count+1}"
        msg += f"\n📊 Prochain : *{next_tf}*"
    msg += f"\n\nQuand tu es prêt → /analyse"

    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    imgs = user_images.get(uid, [])

    if not imgs:
        await update.message.reply_text(
            "❌ Aucun graphique reçu.\n\nEnvoie tes screenshots d'abord, puis /analyse"
        )
        return

    tfs_received = [img["tf"] for img in imgs]
    msg = await update.message.reply_text(
        f"⚡ *Analyse en cours...*\n\n"
        f"📊 {len(imgs)} graphique(s) : {' · '.join(tfs_received)}\n\n"
        f"⏳ Analyse institutionnelle complète...\n"
        f"_(100+ indicateurs · Smart Money · Macro · On-chain · Dérivés · Quant)_",
        parse_mode=ParseMode.MARKDOWN
    )

    # Build content for Claude
    content = []
    for img in imgs:
        content.append({"type": "text", "text": f"═══ TIMEFRAME {img['tf']} ═══"})
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": img["b64"]}
        })

    tf_list = " · ".join(tfs_received)
    content.append({
        "type": "text",
        "text": f"""ANALYSE INSTITUTIONNELLE ULTIME — {len(imgs)} TIMEFRAMES : {tf_list}

Prends en compte ABSOLUMENT TOUT sans exception :
✅ Chaque timeframe analysé individuellement ET globalement
✅ 100+ indicateurs techniques avec valeurs et signaux précis
✅ Smart Money Concepts complets (OB, FVG, Liquidités, Wyckoff, VSA, BOS, CHOCH, OTE)
✅ Toutes les données macro mondiales actuelles de juin 2026
✅ Données on-chain réelles (MVRV 0.41, ETF -3.4Md$, Fear&Greed 13...)
✅ Dérivés complets (OI, Funding, Options, Liquidations, Gamma...)
✅ Actualités, sentiment, Polymarket, COT Report, géopolitique
✅ Calculs quantitatifs avancés (VaR, Sharpe, Sortino, Kelly, probabilités...)
✅ Position institutionnelle exacte (Hedge Fund, Smart Money, Prop Desk)
✅ Entrée précise + TP1/TP2/TP3 + SL + R:R + Kelly + Plan d'exécution complet

Utilise le format de réponse EXACT défini dans tes instructions. Sois exhaustif sur chaque section."""
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
        analysis = data["content"][0]["text"]

        # Send in chunks (Telegram limit 4096 chars)
        chunks = [analysis[i:i+4000] for i in range(0, len(analysis), 4000)]
        for i, chunk in enumerate(chunks):
            if i == 0:
                await msg.edit_text(chunk, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)

        # Reset images after analysis
        user_images[uid] = []
        await update.message.reply_text(
            "✅ *Analyse terminée !*\n\nEnvoie de nouveaux graphiques pour une nouvelle analyse.",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await msg.edit_text(f"❌ Erreur : {str(e)}\n\nRéessaie avec /analyse")

def main():
    print("🚀 AISignal Pro Bot démarré...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aide", aide))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("analyse", analyse))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
