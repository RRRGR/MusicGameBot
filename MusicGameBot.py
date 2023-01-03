# -*- coding: utf-8 -*-

from os import getenv

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("TOKEN")
AU_CHAT_ID = int(getenv("AU_CHAT_ID"))
GC_CHAT_ID = int(getenv("GC_CHAT_ID"))
GG_CHAT_ID = int(getenv("GG_CHAT_ID"))
GS_CHAT_ID = int(getenv("GS_CHAT_ID"))
OO_CHAT_ID = int(getenv("OO_CHAT_ID"))
AU_ROLE_ID = int(getenv("AU_ROLE_ID"))
OO_ROLE_ID = int(getenv("OO_ROLE_ID"))
AU_ID = int(getenv("AU_ID"))
GG_ID = int(getenv("GG_ID"))
OO_ID = int(getenv("OO_ID"))
SPREADSHEET_URL = getenv("SPREADSHEET_URL")
OO_JOIN_COMMENT = getenv("OO_JOIN_COMMENT")

INITIAL_EXTENSIONS = [
    "cogs.Admin",
    "cogs.Downloader",
    "cogs.EarthMC",
    "cogs.Gacha",
    "cogs.IR",
    "cogs.ManageDic",
    "cogs.OtherCommands",
    "cogs.ReadText",
    "cogs.SearchInformation",
    "cogs.Quiz",
]


class MusicGameBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            help_command=None,
            intents=discord.Intents.all(),
        )

    async def setup_hook(self):
        for cog in INITIAL_EXTENSIONS:
            await self.load_extension(cog)
        await self.tree.sync()

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Game(name="Type '!mhelp' for commands")
        )


if __name__ == "__main__":
    MusicGameBot().run(TOKEN)
