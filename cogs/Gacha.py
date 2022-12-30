# -*- coding: utf-8 -*-

from discord.ext import commands
from discord.ext.commands import Bot, Context
import random
import json

class Gacha(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
    @commands.command()
    async def sdvx(self, ctx: Context, *args: str):
        """Send a random SDVX song from LV.13 to LV.20"""

        if len(args) == 0:
            song, lv = self.get_song("sdvx")
            await ctx.send(song)
        else:
            under13 = self.judge_under_lv(args,13)
            above21 = self.judge_above_lv(args,21) 
            if under13 != "none":
                await ctx.send("Lv.13以下は指定できません。")
            if above21 != "none":
                await ctx.send("Lv.21以上の譜面は存在しません。")
            if under13 != "all" and above21 != "all":
                song = self.get_matchlv_sdvxsong(args)
                await ctx.send(song)

    def get_song(self, game: str) -> str:
        """Get a song from the entire dictionary of songs from the json file."""

        with open("Quiz/songlist.json", "r") as f:
            d = json.load(f)
        songdic = d[game]
        song, lv = random.choice(list(songdic.items()))
        return song, lv

    def get_matchlv_sdvxsong(self, arg):
        """"""
        song, lv = self.get_song("sdvx")
        if self.have_samelv(lv,arg):
            return song
        return self.get_matchlv_sdvxsong(arg)

    def judge_under_lv(self, tuple_args, lv):
        judge_lvlist = []
        for _ in tuple_args:
            try:
                judge_lvlist.append(int(_) <= lv)
            except ValueError:
                judge_lvlist.append(False)
        if all(judge_lvlist):
            return "all"
        elif any(judge_lvlist):
            return "any"
        else:
            return "none"

    def judge_above_lv(self, tuple_args, lv):
        judge_lvlist = []
        for _ in tuple_args:
            try:
                judge_lvlist.append(int(_) >= lv)
            except ValueError:
                judge_lvlist.append(False)
        if all(judge_lvlist):
            return "all"
        elif any(judge_lvlist):
            return "any"
        else:
            return "none"
    
    def have_samelv(self, set1: set, set2: set) -> bool:
        """Judge if the song's LV. is same as user's arg"""

        if len(set(set1) & set(set2)) == 0:
            return False
        else:
            return True
    
    @commands.command()
    async def deemo(self, ctx: Context, *args):
        if len(args) == 0:
            song, lv = self.get_song("deemo")
            if len(lv) == 2:
                song += self.hard_or_ex()
            await ctx.send(song)
        else:
            under3 = self.judge_under_lv(args,3)
            above13 = self.judge_above_lv(args,13)
            if under3 != "none":
                await ctx.send("Lv.3以下のHard譜面は存在しません。")
            if above13 != "none":
                await ctx.send("Lv.13以上の譜面は存在しません。")
            if under3 != "all" and above13 != "all":
                song = self.get_matchlv_deemosong(args)
                await ctx.send(song)

        
    def hard_or_ex(self) -> str:
        """Returns Extra or Hard randomly."""

        if random.random() > 0.5:
            return "(Extra)"
        else:
            return "(Hard)"

    def get_matchlv_deemosong(self, arg: str) -> str:
        """Returns a deemo song."""

        song, lv = self.get_song("deemo")
        if len(lv) == 2:
            if "ex" in arg:
                return song + "(Extra)"
            # else:
            #     return song + "(Hard)"
        if self.have_samelv(lv,arg):
            return song
        return self.get_matchlv_deemosong(arg)

    @commands.command()
    async def arcaea(self, ctx: Context, *args: str):
        if len(args) == 0:
            song, lv = self.get_song("arcaea")
            await ctx.send(song)
        else:
            under0 = self.judge_under_lv(args,0)
            above13 = self.judge_above_lv(args,13)
            if under0 != "none":
                await ctx.send("Lv.0以下の譜面は存在しません。")
            if above13 != "none":
                await ctx.send("Lv.13以上の譜面は存在しません。")
            if under0 != "all" and above13 != "all":
                song, lv = self.get_matchlv_arcaeasong(args)
                await ctx.send(song)

    def get_matchlv_arcaeasong(self, arg: str) -> str:
        song, lv = self.get_song("arcaea")
        if self.have_samelv(lv,arg):
            return song, lv
        return self.get_matchlv_arcaeasong(arg)

    
        

async def setup(bot: Bot):
    await bot.add_cog(Gacha(bot))
    