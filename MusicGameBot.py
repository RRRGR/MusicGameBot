# -*- coding: utf-8 -*-

from os import getenv
from dotenv import load_dotenv
from discord.ext import commands
import discord

load_dotenv()
TOKEN = getenv('TOKEN')
AU_CHAT_ID = int(getenv('AU_CHAT_ID'))
GC_CHAT_ID = int(getenv('GC_CHAT_ID'))
GG_CHAT_ID = int(getenv('GG_CHAT_ID'))
GS_CHAT_ID = int(getenv('GS_CHAT_ID'))
OO_CHAT_ID = int(getenv('OO_CHAT_ID'))
AU_ROLE_ID = int(getenv('AU_ROLE_ID'))
OO_ROLE_ID = int(getenv('OO_ROLE_ID'))
AU_ID = int(getenv('AU_ID'))
GG_ID = int(getenv('GG_ID'))
OO_ID = int(getenv('OO_ID'))
SPREADSHEET_KEY = getenv('SPREADSHEET_KEY')
OO_JOIN_COMMENT = getenv('OO_JOIN_COMMENT')

INITIAL_EXTENSIONS = [
    'cogs.Admin',
    'cogs.Downloader',
    'cogs.Gacha',
    'cogs.IR',
    'cogs.ManageDic',
    'cogs.OtherCommands',
    'cogs.ReadText',
    'cogs.SearchInformation',
    'cogs.Quiz'
]

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


for cog in INITIAL_EXTENSIONS:
    bot.load_extension(cog)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Type '!mhelp' for commands"))

bot.run(TOKEN)