# -*- coding: utf-8 -*-

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context

from db.db import MusicGameBotDB


class ManageDic(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = MusicGameBotDB()

    @commands.command()
    async def addword(self, ctx: Context, *args: str):
        """Registers a word and its pronunciation."""

        if len(args) == 2:
            word = args[0]
            pronunciation = args[1]
            self.db.upsert_pronunciation(ctx.guild.id, word, pronunciation)
            await ctx.send(f"{word}を{pronunciation}として覚えたで。")
        elif len(args) > 2:
            await ctx.send("'単語 読み方'の形式で送ってください。")
        else:
            await ctx.send("読み方も送れや。")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def addwordbyadmin(self, ctx: Context, *args: str):
        if len(args) == 3:
            word = args[0]
            pronunciation = args[1]
            self.db.upsert_pronunciation(int(args[2]), word, pronunciation)
            await ctx.send(f"{word}を{pronunciation}として覚えたで。")
        elif len(args) > 3:
            await ctx.send("'単語 読み方 ⚪︎⚪︎'の形式で送ってください。")
        else:
            await ctx.send("読み方も送れや。")

    @commands.hybrid_command()
    @app_commands.describe(arg="the word you want to delete")
    async def dltword(self, ctx: Context, arg: str):
        """Deletes a word and its reading."""

        deleted = self.db.delete_pronunciation(ctx.guild.id, arg)
        if deleted:
            await ctx.send(f"{arg}を削除したで。")
        else:
            await ctx.send("そんな単語登録されてないで。")

    @commands.hybrid_command()
    async def showdict(self, ctx: Context):
        """Show the registered pairs of a word and its reading."""

        word_list = self.db.get_all_words(ctx.guild.id)
        if len(word_list) == 0:
            embed = discord.Embed(
                title="登録単語", description="登録単語がありません。", color=discord.Colour.gold()
            )
        else:
            text = ""
            for word_tuple in word_list:
                word = word_tuple[0]
                pronunciation = word_tuple[1]
                text += f"{word}: {pronunciation}　"
            embed = discord.Embed(
                title="登録単語", description=text, color=discord.Colour.gold()
            )
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(ManageDic(bot))
