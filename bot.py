import logging
import sqlite3
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 
DB_PATH = "foodie_memory.db"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 1. FOOD BRAIN ---
def get_recent_food(limit=5):
    """Queries the restaurant table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name, neighborhood, taste_rating, notes FROM restaurants ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        
        if not rows: return "🍽️ No food spots found."
            
        text = "🍽️ **Fresh Eats:**\n\n"
        for r in rows:
            text += f"• <b>{r[0]}</b> ({r[1]})\n  Rating: {r[2]}/10\n  <i>{r[3]}</i>\n\n"
        return text
    except Exception as e: return f"❌ Error: {e}"

# --- 2. SHOE BRAIN (NEW) ---
def get_shoe_deals(limit=5):
    """Queries the price_history table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Get the most recent prices found
        c.execute("SELECT shoe_name, price, url, currency FROM price_history ORDER BY found_at DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        
        if not rows: return "👟 No shoe deals found yet. Run 'scout.py'!"
            
        text = "👟 **Latest Shoe Intel:**\n\n"
        for r in rows:
            # r[0]=Name, r[1]=Price, r[2]=URL
            price_display = f"${r[1]}" if r[1] > 0 else "Check Site"
            text += f"• <b>{r[0]}</b>\n  Price: {price_display}\n  <a href='{r[2]}'>Link to Store</a>\n\n"
        return text
    except Exception as e: return f"❌ Error: {e}"

# --- 3. THE ROUTER ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="🤖 **Systems Online.**\n• Ask 'Find food' for eats.\n• Ask 'Find shoes' for kicks."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    
    # Simple Logic: Check keywords to decide which "Agent" to call
    if "shoe" in user_text or "run" in user_text or "sneaker" in user_text:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="👟 Checking shoe tracker...")
        response = get_shoe_deals(limit=5)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='HTML')
        
    elif "food" in user_text or "eat" in user_text or "restaurant" in user_text:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🍽️ Checking food black book...")
        response = get_recent_food(limit=5)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='HTML')
        
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❓ I didn't catch that. Try 'Find shoes' or 'Find food'.")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("❌ ERROR: Telegram Token missing.")
        exit()
        
    print("🤖 Bot is Listening...")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()