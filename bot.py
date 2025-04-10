import os
import telebot

# Get token from environment
TOKEN = os.getenv("BOT_TOKEN")  # Bot token from Railway variables
bot = telebot.TeleBot(TOKEN)

# Admin ID
ADMIN_ID = 5806222268

# Game data dictionary with categories
games = {}

# /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Send me a game name or category (e.g. 'simulation games') and I’ll give you details.")

# Multi-line /add_game handler
@bot.message_handler(commands=['add_game'])
def add_game(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to add games.")
        return

    try:
        text_lines = message.text.split('\n')
        name = link = description = ""
        category = []

        for line in text_lines:
            if line.lower().startswith("game name:-"):
                name = line.split(":-", 1)[1].strip().lower()
            elif line.lower().startswith("download here:-"):
                link = line.split(":-", 1)[1].strip()
            elif line.lower().startswith("short intro:-"):
                description = line.split(":-", 1)[1].strip()
            elif line.lower().startswith("category:-"):
                category = line.split(":-", 1)[1].strip().lower().split(",")
            elif description != "":
                description += "\n" + line.strip()

        category = [cat.strip() for cat in category]
        description = description.strip().replace("\n", " ")

        if not name or not link or not description or not category:
            bot.reply_to(message, "❌ Invalid format. Please use this format:\n\n/add_game\nGame Name:- Name\nDownload Here:- link\nShort Intro:- description\nCategory:- category1, category2, category3")
            return

        games[name] = {
            "link": link,
            "description": description,
            "category": category
        }

        bot.reply_to(message, f"✅ Game '{name.title()}' added successfully under categories: {', '.join(category).title()}!")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# /games command
@bot.message_handler(commands=['games'])
def show_games(message):
    if not games:
        bot.reply_to(message, "❌ No games added yet.")
        return

    game_list = "📋 Available Games:\n"
    for game_name in games:
        game_list += f"- {game_name.title()} ({', '.join(games[game_name]['category']).title()})\n"

    bot.reply_to(message, game_list)

# Search game or category
@bot.message_handler(func=lambda message: True)
def handle_input(message):
    text = message.text.strip().lower()

    matching_by_category = [name for name, data in games.items() if any(text in cat for cat in data["category"])]

    if matching_by_category:
        response = f"📂 Games in '{text.title()}' category:\n"
        for game_name in matching_by_category:
            g = games[game_name]
            response += f"\n🎮 {game_name.title()}\n{g['description']}\n🔗 {g['link']}\n"
        bot.send_message(message.chat.id, response)
        return

    if " games" in text:
        category_name = text.replace(" games", "")
        matching_by_category = [name for name, data in games.items() if category_name in data["category"]]

        if matching_by_category:
            response = f"📂 Games in '{category_name.title()}' category:\n"
            for game_name in matching_by_category:
                g = games[game_name]
                response += f"\n🎮 {game_name.title()}\n{g['description']}\n🔗 {g['link']}\n"
            bot.send_message(message.chat.id, response)
            return

    for game_name, game_data in games.items():
        if text in game_name:
            bot.send_message(
                message.chat.id,
                f"🎮 {game_name.title()}\n\n{game_data['description']}\n\n🔗 Download Link:\n{game_data['link']}"
            )
            return

    bot.reply_to(message, "❌ No game or category found. Try another name or category.")

bot.polling()
