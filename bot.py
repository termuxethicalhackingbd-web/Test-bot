import os
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import uvicorn
from config import BOT_TOKEN

PORT = int(os.environ.get("PORT", 8000))
URL = os.environ.get("WEBHOOK_URL")

users = {}

NFTS = [
    "https://via.placeholder.com/150?text=NFT1",
    "https://via.placeholder.com/150?text=NFT2",
    "https://via.placeholder.com/150?text=NFT3",
    "https://via.placeholder.com/150?text=NFT4",
    "https://via.placeholder.com/150?text=NFT5",
]

ADS = [
    "https://libtl.com/show_ad_10115770",
    "https://libtl.com/show_ad_10115771",
    "https://libtl.com/show_ad_10115772",
]

app = ApplicationBuilder().token(BOT_TOKEN).build()
api = FastAPI()

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = users.get(user_id, {"stars":0, "first_dep": True})
    keyboard = [
        [InlineKeyboardButton("🎰 Spin & Win", callback_data="spin")],
        [InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
         InlineKeyboardButton("📤 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🎁 Offers", callback_data="offers"),
         InlineKeyboardButton("🎟 Referral", callback_data="referral")]
    ]
    await update.message.reply_text(
        "💎 Welcome to NFT Spin Bot!\nSpin, earn stars & collect NFTs!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Button click
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    users.setdefault(user_id, {"stars":0, "first_dep": True})
    data = query.data

    if data == "spin":
        keyboard = [
            [InlineKeyboardButton("1 Free Spin / 24h (5-50 stars)", callback_data="free_spin")],
            [InlineKeyboardButton("10 Spin = 900 Stars", callback_data="10_spin")],
            [InlineKeyboardButton("50 Spin = 3000 Stars", callback_data="50_spin")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await query.message.edit_text(
            "🎰 Choose your spin option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "free_spin":
        reward = random.randint(5,50)
        users[user_id]["stars"] += reward
        nft = random.choice(NFTS)
        ad = random.choice(ADS)
        await query.message.edit_text(
            f"🎉 You won {reward} stars!\nNFT: {nft}\nAd: {ad}\nStars Balance: {users[user_id]['stars']}"
        )

    elif data == "10_spin":
        if users[user_id]["stars"] >= 900:
            users[user_id]["stars"] -= 900
            nft_list = random.choices(NFTS, k=10)
            ad = random.choice(ADS)
            await query.message.edit_text(
                f"🎉 10 Spins done!\nNFTs: {', '.join(nft_list)}\nStars left: {users[user_id]['stars']}\nAd: {ad}"
            )
        else:
            await query.message.edit_text("⚠️ Not enough stars!")

    elif data == "50_spin":
        if users[user_id]["stars"] >= 3000:
            users[user_id]["stars"] -= 3000
            nft_list = random.choices(NFTS, k=50)
            ad = random.choice(ADS)
            await query.message.edit_text(
                f"🎉 50 Spins done!\nNFTs: {', '.join(nft_list)}\nStars left: {users[user_id]['stars']}\nAd: {ad}"
            )
        else:
            await query.message.edit_text("⚠️ Not enough stars!")

    elif data == "deposit":
        await query.message.edit_text(
            "💰 Deposit TON:\n- Min: 0.67 TON → 100 Stars\n- 10 TON → 500 Star Bonus\nSend to: UQCDFoAkxjfFc8pCVwNY5Lrn2kZAG8fbCK8NhsoR_7VE9DtA"
        )

    elif data == "withdraw":
        await query.message.edit_text(
            f"📤 Withdraw NFT (Min 5000 Stars required)\nStars Balance: {users[user_id]['stars']}"
        )

    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("🎰 Spin & Win", callback_data="spin")],
            [InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
             InlineKeyboardButton("📤 Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton("🎁 Offers", callback_data="offers"),
             InlineKeyboardButton("🎟 Referral", callback_data="referral")]
        ]
        await query.message.edit_text(
            "💎 Main menu",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))

# FastAPI webhook for Vercel
@api.post(f"/{BOT_TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, app.bot)
    await app.update_queue.put(update)
    return {"status": "ok"}

async def set_webhook():
    await app.bot.set_webhook(f"{URL}/{BOT_TOKEN}")

import asyncio
asyncio.run(set_webhook())

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=PORT)
