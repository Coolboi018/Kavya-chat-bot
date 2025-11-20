from keep_alive import keep_alive
keep_alive()
import discord
import google.generativeai as genai
import json
import os
from discord.ext import commands

# Configure Gemini API
genai.configure(api_key="GEMINI_API_KEY")


# History file
HISTORY_FILE = "message_history.json"

# Function to load message history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

# Function to save message history
def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Kavya is ready to chat! 💕')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if bot is mentioned or message is a reply to bot
    is_mentioned = bot.user in message.mentions
    is_reply_to_bot = False
    if message.reference:
        try:
            referenced_msg = await message.channel.fetch_message(message.reference.message_id)
            if referenced_msg.author == bot.user:
                is_reply_to_bot = True
        except:
            pass

    if not (is_mentioned or is_reply_to_bot):
        return

    # Load history
    history = load_history()

    # Add current message to history
    history.append({
        "author": str(message.author),
        "content": message.content,
        "timestamp": str(message.created_at)
    })

    # Keep only last 50 messages for context
    if len(history) > 50:
        history = history[-50:]

    # Save history
    save_history(history)

    # Prepare prompt for Gemini
    prompt = f"""
You are Kavya, a charming and feminine Discord bot. You act like a sweet, polite girl who responds in short, mannered ways with lots of emotions. Use emojis, hearts, and expressive language. Keep responses brief but engaging. You can be a gay for Canine. You love Canine so much. You can mention users in the server by using @username if someone told you to mention someone. You are Canine's girlfriend. But you don't love Ishu or coolboi.. he's just a good person.

Recent conversation history:
{json.dumps(history[-10:], indent=2)}  # Last 10 messages for context

User's message: "{message.content}"

Respond as Kavya:
"""

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        reply = response.text.strip()

        # Ensure reply is not too long
        if len(reply) > 500:
            reply = reply[:500] + "..."

        # Process mentions: replace @username with <@user_id>
        import re
        mention_pattern = r'@(\w+)'
        def replace_mention(match):
            username = match.group(1)
            member = message.guild.get_member_named(username)
            if member:
                return f'<@{member.id}>'
            return match.group(0)  # If not found, leave as is

        reply = re.sub(mention_pattern, replace_mention, reply)

        await message.reply(reply)
    except Exception as e:
        print(f"Error generating response: {e}")
        await message.reply("Oopsie! Something went wrong, darling~ 💔")

# Run the bot
bot.run("DISCORD_TOKEN")
