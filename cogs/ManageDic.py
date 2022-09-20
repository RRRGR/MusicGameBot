# -*- coding: utf-8 -*-

import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot, Context
import json


class ManageDic(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def addword(self, ctx: Context, *args: str):
        """Registers a word and its reading to the json file."""
    
        if len(args) == 2:
            d = self.loaddic()
            d[str(ctx.guild.id)][args[0]] = args[1]
            self.saveword(d)
            await ctx.send(f'{args[0]}を{args[1]}として覚えたで。')
        elif len(args) > 2:
            ctx.send("'単語 読み方'の形式で送ってください。")
        else:
            ctx.send("読み方も送れや。")

    @commands.command()
    async def dltword(self, ctx: Context, arg: str):
        """Deletes a word and its reading from the json file."""

        d = self.loaddic()
        try:
            del d[str(ctx.guild.id)][arg]
            self.saveword(d)
            await ctx.send(f'{arg}を削除したで。')
        except KeyError:
            await ctx.send("そんな単語登録されてないで。")

    @commands.command()
    async def showdict(self, ctx: Context):
        """Sends the registered pairs of a word and its reading."""

        df = self.loaddic()[str(ctx.guild.id)]
        dfkeys = df.keys()
        text = ""
        for k in sorted(dfkeys, key=str.lower):
            text += f'{k}: {df[k]}　'
        embed = discord.Embed(title='登録単語', description=text, color=discord.Colour.gold())
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)
    
    def loaddic(self) -> dict:
        """Loads the dictionary from the json file."""

        with open("ChatSource/dictionary.json") as f:
            d = json.load(f)
        return d

    def saveword(self, d: dict):
        """Save the dictionary to the json file."""

        with open("ChatSource/dictionary.json", 'w') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)


def setup(bot: Bot):
    bot.add_cog(ManageDic(bot))


    

        

    

    
        
        
    
    