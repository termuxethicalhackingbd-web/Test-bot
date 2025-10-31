# bot.py

import random
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, CHANNEL_USERNAME, DEPOSIT_ADDRESS, NFT_IMAGES

# Database setup
conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, stars INTEGER DEFAULT 0, last_free_spin TEXT)''')
conn.commit()

# Utility functions
def get_user(user_id):
    c.execute("SELECT stars FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO users(user_id, stars) VALUES (?,0)", (user_id,))
        conn.commit()
        return 0

def add_stars(user_id, amount):
    stars = get_user(user_id) + amount
    c.execute("UPDATE users SET stars=? WHERE user_id=?", (stars, user_id))
    conn.commit()
    return stars

def deduct_stars(user_id, amount):
    stars = get_user(user_id)
    if stars >= amount:
        stars -= amount
        c.execute("UPDATE users SET stars=? WHERE user_id=?", (stars, user_id))
        conn.commit()
        return True, stars
    return False, stars

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_stars(user_id, 0)  # ensure user exists
    text = (
        "💎 *Welcome to Ultra Max Pro NFT Spin Bot!*\n\n"
        "🎯 Spin daily and win NFT rewards!\n"
        "💰 Earn Stars and withdraw NFT anytime.\n\n"
        f"🌍 Please join our channel {CHANNEL_USERNAME} for updates (optional)."
    )
    keyboard = [
        [InlineKeyboardButton("🎰 Spin & Win", callback_data="spin"),
         InlineKeyboardButton("💰 Deposit", callback_data="deposit")],
        [InlineKeyboardButton("📤 Withdraw", callback_data="withdraw"),
         InlineKeyboardButton("💎 Balance", callback_data="balance")],
        [InlineKeyboardButton("🎁 Offers", callback_data="offers"),
         InlineKeyboardButton("🎟 Referral", callback_data="referral")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Main menu builder
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 Spin & Win", callback_data="spin"),
         InlineKeyboardButton("💰 Deposit", callback_data="deposit")],
        [InlineKeyboardButton("📤 Withdraw", callback_data="withdraw"),
         InlineKeyboardButton("💎 Balance", callback_data="balance")],
        [InlineKeyboardButton("🎁 Offers", callback_data="offers"),
         InlineKeyboardButton("🎟 Referral", callback_data="referral")]
    ])

# Spin submenu
async def spin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    stars = get_user(user_id)
    keyboard = [
        [InlineKeyboardButton("Free Spin (24h) 🎯", callback_data="free_spin")],
        [InlineKeyboardButton("1 Spin = 100⭐", callback_data="spin1"),
         InlineKeyboardButton("10 Spins = 900⭐", callback_data="spin10")],
        [InlineKeyboardButton("50 Spins = 3000⭐", callback_data="spin50")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ]
    text = f"🎰 *Choose Spin Option:*\n\n💫 Your Stars: {stars}"
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Handle spins
async def handle_spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    reward = 0

    if data == "free_spin":
        reward = random.randint(5,50)
        add_stars(user_id, reward)
        nft_image = random.choice(NFT_IMAGES)
        await query.edit_message_text(f"🎉 Free Spin Reward: {reward}⭐\nNFT Reward:", parse_mode="Markdown")
        await context.bot.send_photo(chat_id=user_id, photo=nft_image)
    elif data == "spin1":
        success, stars = deduct_stars(user_id, 100)
        if not success:
            await query.edit_message_text("⚠️ Not enough Stars!")
            return
        reward = random.randint(5,50)
        add_stars(user_id, reward)
        nft_image = random.choice(NFT_IMAGES)
        await query.edit_message_text(f"🎉 1 Spin Used: Reward {reward}⭐\nNFT Reward:", parse_mode="Markdown")
        await context.bot.send_photo(chat_id=user_id, photo=nft_image)
    elif data == "spin10":
        success, stars = deduct_stars(user_id, 900)
        if not success:
            await query.edit_message_text("⚠️ Not enough Stars!")
            return
        for _ in range(10):
            reward += random.randint(5,50)
        add_stars(user_id, reward)
        nft_image = random.choice(NFT_IMAGES)
        await query.edit_message_text(f"🎉 10 Spins Used: Total Reward {reward}⭐\nNFT Reward:", parse_mode="Markdown")
        await context.bot.send_photo(chat_id=user_id, photo=nft_image)
    elif data == "spin50":
        success, stars = deduct_stars(user_id, 3000)
        if not success:
            await query.edit_message_text("⚠️ Not enough Stars!")
            return
        for _ in range(50):
            reward += random.randint(5,50)
        add_stars(user_id, reward)
        nft_image = random.choice(NFT_IMAGES)
        await query.edit_message_text(f"🎉 50 Spins Used: Total Reward {reward}⭐\nNFT Reward:", parse_mode="Markdown")
        await context.bot.send_photo(chat_id=user_id, photo=nft_image)
    
    await spin_menu(update, context)  # back to spin menu

# Callback handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "spin":
        await spin_menu(update, context)
    elif data in ["free_spin","spin1","spin10","spin50"]:
        await handle_spin(update, context)
    elif data == "balance":
        user_id = query.from_user.id
        stars = get_user(user_id)
        text = f"💎 Your Stars Balance: {stars}"
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "deposit":
        text = f"💰 Deposit TON:\nMinimum: 0.67 TON\nAddress:\n`{DE