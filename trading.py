import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["8638934247:AAE1HCR938-b1RhNUUaa4yLHq7KE5t5Pgaw"]


def get_value(text, keys):
    for key in keys:
        pattern = rf"{key}\s*[:=]?\s*([0-9.]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot is alive ✅\n\n"
        "Quick format:\n"
        "/trade 4256 4310 0.10\n\n"
        "Full calculator:\n"
        "/calc buy\n"
        "entry=4256\n"
        "sl=4200\n"
        "tp=4380\n"
        "spread=2\n"
        "lot=0.10\n"
        "pip=10"
    )


async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        buy = float(context.args[0])
        sell = float(context.args[1])
        lot = float(context.args[2])
        pips = abs(sell - buy)

        message = f"""
📈 Trade Setup

🟢 Buy Point: {buy}
🔴 Sell Point: {sell}

📏 Pips: {pips:.2f}
📦 Lot Size: {lot}

⚖️ Risk : Reward: 1 : 2
"""
        await update.message.reply_text(message)

    except:
        await update.message.reply_text(
            "Use format:\n/trade 4256 4310 0.10"
        )


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text

        direction = "BUY" if "buy" in text.lower() else "SELL"

        entry = get_value(text, ["entry"])
        sl = get_value(text, ["sl", "stop", "stoploss"])
        tp = get_value(text, ["tp", "target", "takeprofit"])
        spread = get_value(text, ["spread"])
        lot = get_value(text, ["lot", "size"])
        pip_value = get_value(text, ["pip", "pipvalue"])

        if None in [entry, sl, tp, spread, lot, pip_value]:
            raise ValueError

        raw_risk_pips = abs(entry - sl)
        raw_reward_pips = abs(tp - entry)

        risk_pips = raw_risk_pips + spread
        reward_pips = raw_reward_pips - spread

        if reward_pips <= 0:
            await update.message.reply_text("Reward pips must be bigger than spread.")
            return

        rr = reward_pips / risk_pips

        possible_loss = risk_pips * lot * pip_value
        possible_win = reward_pips * lot * pip_value

        message = f"""
📊 Trade Calculator

Direction: {direction}

📍 Entry: {entry}
🛑 Stop Loss: {sl}
🎯 Take Profit: {tp}

📌 Spread: {spread} pips
📦 Lot Size: {lot}
💵 Pip Value: ${pip_value}

📉 Pips to Lose: {risk_pips:.2f}
📈 Pips to Win: {reward_pips:.2f}

💸 Possible Loss: ${possible_loss:.2f}
💰 Possible Win: ${possible_win:.2f}

⚖️ Risk : Reward = 1 : {rr:.2f}
"""
        await update.message.reply_text(message)

    except:
        await update.message.reply_text(
            "Use format:\n\n"
            "/calc buy\n"
            "entry=4256\n"
            "sl=4200\n"
            "tp=4380\n"
            "spread=2\n"
            "lot=0.10\n"
            "pip=10"
        )


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("trade", trade))
app.add_handler(CommandHandler("calc", calc))

print("Bot is running...")
app.run_polling(drop_pending_updates=True)