from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TOKEN

# User data storage
users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = users.get(user_id, {"stars": 0})

    text = (
        "💎 *Welcome to NFT Spin Bot!*\n\n"
        "🎯 Spin daily and win NFT rewards!\n"
        "💰 Earn Stars and withdraw NFT anytime.\n\n"
        "🌍 *Please connect VPN before using the bot.*"
    )

    keyboard = [
        [InlineKeyboardButton("🎰 Spin & Win", callback_data="spin"),
         InlineKeyboardButton("💰 Deposit", callback_data="deposit")],
        [InlineKeyboardButton("🎁 Offers", callback_data="offers"),
         InlineKeyboardButton("🎟 Referral", callback_data="referral")],
        [InlineKeyboardButton("📤 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "spin":
        await query.edit_message_text("🎰 Choose spin option:\n1 Free spin per 24 hours.\n💫 1 Spin = 100 Stars\n💫 15 Spins = 1000 Stars\n💫 50 Spins = 3000 Stars\n⚠️ After spin, Ads will appear automatically!")
    elif query.data == "deposit":
        await query.edit_message_text("💰 Deposit TON to get Stars.\nMinimum deposit: 0.67 TON = 100 Stars\n10 TON deposit = 500 Stars bonus")
    elif query.data == "offers":
        await query.edit_message_text("🎁 Check available offers here!")
    elif query.data == "referral":
        await query.edit_message_text("🎟 Share your referral link and earn 10 Stars per referral!")
    elif query.data == "withdraw":
        await query.edit_message_text("📤 Withdraw NFT\nMinimum: 5000 Stars")
    elif query.data == "back":
        await start(update, context)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
