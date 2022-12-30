# -*- coding: utf-8 -*-

import discord
from discord import channel
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone
import datetime
import asyncio
import pandas as pd
import re
from MusicGameBot import SPREADSHEET_KEY

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']

json = 'spread-sheet-350909-94d641982b67.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json, scope)
gc = gspread.authorize(credentials)

class IR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(hidden=True)
    async def ir(self, ctx: commands.Context, *args):
        id = self.bot.get_channel(ctx.message.guild)
        if len(args) == 0:
            embed = discord.Embed(title='IR概要: https://docs.google.com/spreadsheets/d/1C09UnShrHIwbTAdNc6cydr3ySNGWl6k3XbS9uxRU5Oo/edit?usp=sharing', url='https://docs.google.com/spreadsheets/d/1C09UnShrHIwbTAdNc6cydr3ySNGWl6k3XbS9uxRU5Oo/edit?usp=sharing')
            embed.add_field(name='スコアの提出方法', value="!ir [機種] [コースNo.] [左or右] [スコア] の書式でコマンドを送信\n誤ってコマンドを入力したら正しいコマンドでもう一度送信してください(それか運営に伝えてくれれば手動でスプシを更新します)。", inline=False)
            embed.add_field(name='機種', value="機種名は'arcaea','プロセカ','バンドリ','deemo','cytus','cytus2','voez','phigros','lanota','オバラピ','グルミク','unbeatable','osu','bms'の文字列を使用してください。", inline=False)
            embed.add_field(name='コースNo.', value='課題曲一覧のスプシにある番号', inline=False)
            embed.add_field(name='左or右', value='課題曲一覧のスプシで曲がB列にあったら左、C列だったら右を入力します。', inline=False)
            embed.add_field(name='スコア', value='機種ごとに求められているスコアを自分で計算して入力してください。')
            return await ctx.send(embed=embed)

        if len(args) == 1:
            async with ctx.typing():
                embed = self.get_rank(args)
            if embed == 1:
                return await ctx.send('機種名を正しく入力してください。')
            return await ctx.send(embed=embed)

        if len(args) == 2:
            if args[1] == 'link':
                try:
                    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(args[0].lower())
                except gspread.exceptions.WorksheetNotFound:
                    return await ctx.send('機種名を正しく入力してください。')
                criteria_re = re.compile("https?://[\w!?/+\-_~;.,*&@#$%()'[\]]+")
                cell_list = worksheet.findall(criteria_re)
                links = ''
                for cell in cell_list:
                    links += f'\n{cell.value}'
                return await ctx.send(links)

        if not ctx.message.attachments:
            return await ctx.send('スクショと一緒に投稿してください。')
        if len(args) != 4:
            return await ctx.send('書式が間違っています。!ir [機種] [コースNo.] [左or右] [スコア] の書式で送ってください。')

        score_error = self.catch_scoreerror(args)
        if score_error == 1:
            return await ctx.send('不正なスコアです。')
        elif score_error == 2:
            return await ctx.send('提出制限のスコアに達していません。')

        course_error = self.catch_courseerror(args)
        if course_error == 1:
            return await ctx.send('コース番号が違います。')
        
        try:
            worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(args[0].lower())
        except gspread.exceptions.WorksheetNotFound:
            return await ctx.send('機種名を正しく入力してください。')
        try:
            exitcode = await self.update_score(ctx, args, worksheet)
        except Exception as e:
            print(e)
            return await ctx.send('エラーが発生しました。')
        if exitcode == 1:
            return await ctx.send('曲の指定(左or右)が間違っています。')
        
        await ctx.message.add_reaction('👍')

    def get_rank(self, args: tuple) -> discord.Embed:
        model = args[0].lower()
        embed = discord.Embed(title=f'{model} IRランキング')
        
        def get_courserank(model: str, coursenum: int) -> str:
            try:
                worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(model)
            except gspread.exceptions.WorksheetNotFound:
                return 'None'
            name_index = coursenum*9 - 6
            name_list = worksheet.col_values(name_index)
            score_list = worksheet.col_values(name_index+1)
            course_rank = ''
            if len(name_list) <= 2:
                course_rank = 'スコアが登録されていません。'
                return course_rank
            for i in range(2,len(name_list)):
                if i == 2:
                    diff_max = (int(float(score_list[0])*100) - int(float(score_list[i])*100)) / 100
                    if diff_max == 0:
                        diff_max = 'MAX'
                    else:
                        diff_max = f'MAX-{str(diff_max)}'
                    course_rank += f'{i-1}. {name_list[i]}: {score_list[i]} ({diff_max})'
                else:
                    diff = (int(float(score_list[i-1])*100) - int(float(score_list[i])*100)) / 100
                    course_rank += f'\n{i-1}. {name_list[i]}: {score_list[i]} (-{str(diff)})'
            return course_rank
        
        if model == 'arcaea':
            for i in range(1,7):
                rank = get_courserank(model, i)
                embed.add_field(name=f'コース{i}', value=rank, inline=False)
        elif model == 'プロセカ':
            for i in range(1,6):
                rank = get_courserank(model, i)
                embed.add_field(name=f'コース{i}', value=rank, inline=False)
        elif model == 'グルミク':
            for i in range(1,5):
                rank = get_courserank(model, i)
                embed.add_field(name=f'コース{i}', value=rank, inline=False)
        else:
            for i in range(1,3):
                rank = get_courserank(model, i)
                embed.add_field(name=f'コース{i}', value=rank, inline=False)

        return embed

    async def update_score(self, ctx: commands.Context, args, worksheet):
        author = str(ctx.author)[:-5]
        date = ctx.message.created_at + datetime.timedelta(hours=9)
        date = date.strftime('%Y-%m-%d %H:%M:%S')
        url = ctx.message.jump_url
        model = args[0].lower()
        coursenum = int(args[1])
        whichsong = args[2]
        score = args[3]
        
        
        authcol = 9*coursenum - 6
        for i in range(3,100):
            cell_author = worksheet.cell(i,authcol).value
            if cell_author is None:
                break
            if cell_author == author:
                break   
            await asyncio.sleep(1)      
        row = i
        await asyncio.sleep(1)

        
        if whichsong == '左':
            worksheet.update_cell(row, authcol, author)
            worksheet.update_cell(row, authcol+2, score)
            worksheet.update_cell(row, authcol+4, date)
            worksheet.update_cell(row, authcol+5, url)
            return 0
        elif whichsong == '右':
            worksheet.update_cell(row, authcol, author)
            worksheet.update_cell(row, authcol+3, score)
            worksheet.update_cell(row, authcol+4, date)
            worksheet.update_cell(row, authcol+6, url)
            return 0
        else:
            return 1

    def catch_scoreerror(self, args):
        model = args[0].lower()
        try:
            score = float(args[3])
        except ValueError:
            return 1
        if model == 'arcaea':
            if score >= 10005000:
                return 1
            if score < 9800000:
                return 2
        if model == 'プロセカ':
            if score >= 3000:
                return 1
        if model == 'バンドリ':
            if score >= 4000:
                return 1
        if model == 'deemo':
            if score >= 1261:
                return 1
        if model == 'cytus':
            if score > 100:
                return 1
        if model == 'cytus2':
            if score > 100:
                return 1
        if model == 'voez':
            if score >= 5000:
                return 1
        if model == 'phigros':
            if score > 100:
                return 1
        if model == 'lanota':
            if score >= 5000:
                return 1
        if model == 'オバラピ':
            if score > 1000000:
                return 1
        if model == 'グルミク':
            if score > 4000:
                return 1
        if model == 'unbeatable':
            if score > 300:
                return 1
        if model == 'osu':
            if score > 1000000:
                return 1
        if model == 'bms':
            if score > 15000:
                return 1
        return 0

    def catch_courseerror(self, args):
        model = args[0].lower()
        try:
            coursenum = int(args[1])
        except ValueError:
            return 1
        if model == 'arcaea':
            if coursenum > 6:
                return 1
        elif model == 'プロセカ':
            if coursenum > 5:
                return 1
        elif model == 'グルミク':
            if coursenum > 4:
                return 1
        else:
            if coursenum > 2:
                return 1
        return 0



    async def sort_sheet(self, args, worksheet):
        model = args[0].lower()
        coursenum = int(args[1])
        authcol = 9*coursenum - 6
        if authcol <= 26:
            alphabet_1 = chr(authcol+64)
        else:
            alphabet_1 = f'A{chr(authcol+64-26)}'
        if authcol <= 20:
            alphabet_2 = chr(authcol+70)
        elif authcol <= 46:
            alphabet_2 = f'A{chr(authcol+70-26)}'
        else:
            alphabet_2 = f'B{chr(authcol+70-52)}'
        #worksheet.sort((authcol+4,'asc'), range=f'{alphabet_1}3:{alphabet_2}30')
        asyncio.sleep(2)
        worksheet.sort((authcol+1,'des'), range=f'{alphabet_1}3:{alphabet_2}30')


        

        

async def setup(bot):
    await bot.add_cog(IR(bot))