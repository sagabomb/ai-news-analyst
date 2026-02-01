import logging
import sqlite3
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 
DB_PATH = "foodie_memory.db"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- DATABASE FUNCTION ---
def get_recent_finds(limit=5):
    """Queries the database using YOUR EXACT SCHEMA."""
    if not os.path.exists(DB_PATH):
        return "⚠️ Database not found! Run the sentinel script first."
        
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # VERIFIED QUERY: Uses only 'name', 'neighborhood', 'taste_rating', 'notes'
        c.execute("SELECT name, neighborhood, taste_rating, notes FROM restaurants ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            return "No new discoveries yet."
            
        text = "🍽️ **Latest Discoveries:**\n\n"
        for r in rows:
            # r[0]=name, r[1]=neighborhood, r[2]=rating, r[3]=notes
            # Using 'notes' as the description since 'cuisine' doesn't exist
            text += f"• <b>{r[0]}</b> ({r[1]})\n  Rating: {r[2]}/10\n  <i>{r[3]}</i>\n\n"
        return text
    except Exception as e:
        return f"❌ Database Error: {e}"

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="🕵️‍♂️ **Foodie Sentinel Online.**\nAsk me: 'What did you find?'"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    
    if "find" in user_text or "food" in user_text or "new" in user_text:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🔍 Checking the Black Book...")
        response = get_recent_finds()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='HTML')
        
    elif "shoe" in user_text:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="👟 Shoe Tracker coming in Project 2!")
        
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I only know about food! Ask me 'What did you find?'")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("❌ ERROR: Telegram Token missing in .env")
        exit()
        
    print("🤖 Bot is Listening...")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()