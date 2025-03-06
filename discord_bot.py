import discord
from discord.ext import commands, tasks
import asyncio
import openai  # Using OpenAI API as an alternative to Google Gemini
import yt_dlp  # For music playback
import os
from dotenv import load_dotenv  # Load environment variables

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not OPENAI_API_KEY or not DISCORD_BOT_TOKEN:
    raise ValueError("Missing API keys! Please check your .env file.")

# Intents and bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True  # Required for member joins
intents.presences = True  # Required for presence updates
intents.message_content = True  # Required for reading message content

bot = commands.Bot(command_prefix="!", intents=intents)

# Chat using OpenAI API
@bot.command()
async def chat(ctx, *, message: str):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini", 
        messages=[{"role": "user", "content": message}],
        temperature=0.7
    )
    await ctx.send(response["choices"][0]["message"]["content"])

# Reminder system
reminders = []

@bot.command()
async def remind(ctx, time: int, *, reminder: str):
    await ctx.send(f"Reminder set for {time} seconds!")
    await asyncio.sleep(time)
    await ctx.send(f"Reminder: {reminder}")

# Poll system
@bot.command()
async def poll(ctx, question: str, *options):
    if len(options) < 2:
        await ctx.send("A poll needs at least two options!")
        return
    
    embed = discord.Embed(title=question, color=discord.Color.blue())
    description = ""
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    
    for i, option in enumerate(options):
        if i >= len(reactions):
            break  # Prevents errors if more than 5 options are given
        description += f"{reactions[i]} {option}\n"
    embed.description = description
    
    message = await ctx.send(embed=embed)
    for i in range(min(len(options), len(reactions))):
        await message.add_reaction(reactions[i])

# Music system
@bot.command()
async def play(ctx, url: str):
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("Join a voice channel first!")
        return
    
    vc = await voice_channel.connect()
    ydl_opts = {'format': 'bestaudio'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
    
    vc.play(discord.FFmpegPCMAudio(url2), after=lambda e: asyncio.run_coroutine_threadsafe(vc.disconnect(), bot.loop))
    await ctx.send(f"Playing: {info['title']}")

# Custom welcome message
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome {member.mention} to the server!")

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)