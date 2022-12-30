# -*- coding: utf-8 -*-

import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot, Context
import json
import requests
import urllib
from bs4 import BeautifulSoup
import re
import pandas
from pandas import DataFrame

class SearchInformation(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.searchable_models = ['sdvx', 'deemo', 'arcaea']
        
    @commands.command()
    async def sch(self, ctx: Context, *args: str):
        if args[-1].lower() in self.searchable_models:
            model = args[-1]
            songname = " ".join(str(i) for i in args[:-1])
            song_candidate_list, model = self.search_songlist(songname, model)
        else:
            songname = " ".join(str(i) for i in args)
            song_candidate_list, model = self.search_songlist(songname)

        if song_candidate_list is None:
            embed = discord.Embed(title=songname,description='Nothing was found.',color=discord.Colour.blue())
        elif len(song_candidate_list) == 1:
            embed = self.get_embed(song_candidate_list[0], model)
        else:
            song_candidates = "\n".join(song_candidate_list)
            embed = discord.Embed(title=songname,description=song_candidates,color=discord.Colour.blue())
        await ctx.send(embed=embed)

    def search_songlist(self, songname: str, model=None):
        with open("Quiz/songlist.json", "r") as f:
            songlist = json.load(f)
        song_candidate = []
        if model is None:
            for model in self.searchable_models:
                for song in songlist[model]:
                    if songname.lower() in song.lower():
                        song_candidate.append(song)
                if len(song_candidate) > 0:
                    break
        else:
            for song in songlist[model]:
                if songname.lower() in song.lower():
                    song_candidate.append(song)
        if len(song_candidate) > 0:
            return song_candidate, model
        else:
            return None, None

    def get_embed(self, song: str, model: str) -> Embed:
        if model == "deemo":
            embed = self.set_deemo_info(song)
        if model == "sdvx":
            embed = self.set_sdvx_info(song)
        if model == "arcaea":
            embed = self.set_arcaea_info(song)
        return embed
    
    def creat_wikiurl(self, gamemodel: str, songname: str) -> str:
        url = "https://wikiwiki.jp/"
        url += urllib.parse.quote(gamemodel+"/"+songname)
        return url

    def get_df(self, url: str) -> DataFrame:
        fetched_dataframes = pandas.io.html.read_html(url, encoding='utf-8')
        df = fetched_dataframes[0]
        return df

    def make_embed(self, url: str) -> Embed:
        embed = discord.Embed(title="result",color=discord.Colour.blue(),url=url)
        return embed

    def set_deemo_info(self, song: str) -> Embed:
        url = self.creat_wikiurl("deemo", song)
        df = self.get_df(url)
        embed = discord.Embed(title="Result (click here to see the wiki page)",color=discord.Colour.blue(),url=url)
        embed.set_author(name='Deemo', url='https://apps.apple.com/jp/app/deemo/id700637744?uo=4', icon_url='https://is1-ssl.mzstatic.com/image/thumb/Purple125/v4/21/64/9a/21649a6e-143c-be37-10fb-73aa0106b6f3/source/100x100bb.jpg')
        level_notes = self.get_deemo_level_notes(df)
        embed.add_field(name="Level, Notes", value=level_notes)
        for index,row in df[2:].iterrows():
            embed.add_field(name=str(row[0]), value=row[1])
        return embed

    def get_deemo_level_notes(self, df: DataFrame) -> str:
        level_notes = ""
        for column_name, item in df.loc[:, "Easy":].iteritems():
            level_notes_val = f'{str(column_name)}: {item[0]}, {item[1]} \n'
            level_notes += level_notes_val
        return level_notes

    def get_arcaea_level_notes(self, df: DataFrame) -> str:
        arcaea_levels = ['Past', 'Present', 'Future', 'Beyond']
        level_notes = ""
        for column_name, item in df[2:5].iloc[:, 2:].iteritems():
            if item.iloc[0] not in arcaea_levels:
                break
            LNval = f'{str(item.iloc[0])}: {item.iloc[1]}, {item.iloc[2]} \n'
            level_notes += LNval
        return level_notes

    def set_arcaea_info(self, song: str) -> Embed:
        url = self.creat_wikiurl("arcaea", song)
        df = self.get_df(url)
        embed = discord.Embed(title="Result (clicke here to see the wiki page)",color=discord.Colour.blue(),url=url)
        embed.set_author(name='Arcaea', url='https://apps.apple.com/us/app/arcaea/id1205999125?uo=4', icon_url='https://is5-ssl.mzstatic.com/image/thumb/Purple125/v4/80/6d/cf/806dcf4e-f68f-4ec0-d63b-01fa624346ba/source/100x100bb.jpg')
        level_notes = self.get_arcaea_level_notes(df)
        embed.add_field(name="Level, Notes", value=level_notes)
        embed = self.set_arcaea_other_infos(df, embed)
        return embed

    def set_arcaea_other_infos(self, df: DataFrame, embed: Embed) -> Embed:
        for index,row in df.iterrows():
            if (row[0] == "Difficulty"
            or row[0] == "Level"
            or row[0] == "Notes"):
                continue
            else:
                if row[0] != row[1]:
                    embed.add_field(name=row[0]+' '+row[1], value=row[2])
                else:
                    embed.add_field(name=row[0], value=row[2])
        return embed

    def get_sdvx_songpage(self, song: str):
        songlist_page_url = 'https://w.atwiki.jp/sdvx/pages/8759.html'
        html = requests.get(songlist_page_url)
        soup = BeautifulSoup(html.content, "html.parser")
        titles = soup.find_all(href=re.compile('atwiki'))
        for title in titles:
            title_name = title.get('title')
            if title_name != None and song in title_name:
                url = title.get('href')
                return "https:" + url
        return None

    def get_sdvx_df(self, url: str) -> DataFrame:
        dfs = pandas.io.html.read_html(url, encoding='utf-8')
        for df in dfs:
            if len(df) > 1:
                break
        return df

    def set_sdvx_info(self, song: str):
        url = self.get_sdvx_songpage(song)
        if url != None:
            df = self.get_sdvx_df(url)
            level_notes = self.get_sdvx_level_notes(df)
            embed = discord.Embed(title="Result (click here to see the wiki page)", color=discord.Colour.blue(),url=url)
            embed.set_author(name='SOUND VOLTEX',url='https://p.eagate.573.jp/game/sdvx/vi/', icon_url='https://eacache.s.konaminet.jp/game/sdvx/vi/images/menu/logo.png')
            embed.add_field(name="Level, Notes", value=level_notes)
            for column_name,item in df.iloc[:,3:].iteritems():
                embed.add_field(name=str(column_name), value=item[0])
            return embed
        return None
            

    def get_sdvx_level_notes(self, df: DataFrame):
        level_notes = ""
        for i in range(len(df)):
            df_row = df[i:i+1]
            level_notes += "{}: {}, {}\n".format(df_row.iat[0,0],df_row.iat[0,1],df_row.iat[0,2])
        return level_notes



async def setup(bot: Bot):
    await bot.add_cog(SearchInformation(bot)) 