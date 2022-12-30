# -*- coding: utf-8 -*-

import asyncio
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from collections import defaultdict
import html
import urllib
import re
import glob
from discord.ext import commands
from discord.ext.commands import Bot, Context

class Downloader(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.dls = DLsonglist()
        self.dli = DLimage()
        
    @commands.is_owner()
    @commands.command(hidden=True)
    async def songlist(self, ctx: Context, model: str):
        if model == "deemo":
            dic = self.dls.get_deemodic()
        elif model == "arcaea":
            dic = self.dls.get_arcaeadic()
        elif model == "sdvx":
            dic = self.dls.get_sdvxdic()
        else:
            await ctx.send("Specify a model.")
            return
        self.dls.savedic_tojson("Quiz/songlist.json", model, dic)
        await ctx.send(f'Successfully downloaded {model}\'s songlist.')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def image(self, ctx: Context, model: str):
        if model == "arcaea":
            await self.dli.dl_arcaeaimage(ctx)
        elif model == "sdvx":
            for level in range(13, 21):
                await ctx.send(f'Level {level}')
                await self.dli.dl_sdvximage(ctx, level)
        elif model == "deemo":
            await self.dli.dl_deemoimage(ctx)
        
        await ctx.send(f'Successfully downloaded {model}\'s images.')

class DLsonglist():

    def savedic_tojson(self, filename, model, listname):
        with open(filename) as f:
            d = json.load(f)
        d[model] = listname
        with open(filename, "w") as f:
            json.dump(d,f,ensure_ascii=False)

    def get_deemodic(self):
        deemodic = {}
        url = "https://wikiwiki.jp/deemo/%E6%9B%B2%E5%90%8D%E3%83%AA%E3%82%B9%E3%83%88"
        df = pd.io.html.read_html(url)
        for _ in df:
            if "曲名" in _.columns:
                for data in _.itertuples():
                    deemolevel = []
                    deemolevel.append(str(data.Hard))
                    if "Extra" in _.columns:
                        if data.Extra != "-":
                            deemolevel.append(data.Extra)
                    deemodic[data.曲名] = deemolevel
        return deemodic

    def get_arcaeadic(self):
        arcaeadic = defaultdict(list)
        levellist = []
        url = 'https://wikiwiki.jp/arcaea/%E3%83%AC%E3%83%99%E3%83%AB%E9%A0%86'
        df = pd.io.html.read_html(url)
        for _ in df[0]["Level"]:
            if not pd.isnull(_):
                levellist.append(str(_).replace("Level ", ""))
        counter = -1
        for _ in df:
            if "Song" in _.columns:
                for data in _["Song"]:
                    if pd.isnull(data):
                        continue
                    elif "譜面" in data:
                        continue
                    try:
                        arcaeadic[data.replace("エイプリルフール限定楽曲", "")].append(levellist[counter])
                    except IndexError:
                        break

                counter += 1
        #arcaeadic.pop("init()")
        return arcaeadic

    def get_sdvxdic(self):
        sdvxdic = defaultdict(list)
        levellist = ["20", "19", "18", "17", "16", "15", "14"]
        for i in levellist:
            level = str(i)
            url = f'https://www.sdvx.in/sort/sort_{level}.htm'
            html1 = requests.get(url)
            soup = BeautifulSoup(html1.content, "html.parser")
            elms = soup.find_all('script')
            songlist = [_.next_sibling.next_sibling for _ in elms if _.next_sibling.next_sibling != '\n' and _.next_sibling.next_sibling != None and '<script' not in str(_.next_sibling.next_sibling)]
            for _ in songlist:
                songname = html.unescape(_)
                sdvxdic[songname].append(level)
            #await asyncio.sleep(0.5)
        
        return sdvxdic

class DLimage():
    def download_file(self, url, dst_path):
        try:
            with urllib.request.urlopen(url) as web_file, open(dst_path, 'wb') as local_file:
                local_file.write(web_file.read())
        except urllib.error.URLError as e:
            print(e)
    
    def download_file_with_headers(self, url, dst_path):
        headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
                }

        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request) as web_file, open(dst_path, 'wb') as local_file:
                local_file.write(web_file.read())
        except urllib.error.URLError as e:
            print(e)

    def convert_half_letter(self, text: str) -> str:
        text = text.replace("/", "／")
        text = text.replace(":", "：")
        text = text.replace("¥", "￥")
        text = text.replace("*", "＊")
        text = text.replace("?", "？")
        text = text.replace("<", "＜")
        text = text.replace(">", "＞")
        text = text.replace("|", "｜")
        if text[0] == ".":
            text = f'．{text[1:]}'
        return text

    def get_diff(self, model):
        imagelist = glob.glob(f'Quiz/{model}image/*')
        imagelist = [_.replace(f'Quiz/{model}image/','').replace('.jpg','').replace('.png','') for _ in imagelist]
        with open("Quiz/songlist.json") as f:
            d = json.load(f)
        modeldic = d[model]
        union_song = set(modeldic.keys()) - set(imagelist)
        print(union_song)
        return union_song

    def get_diff_sdvx(self, songdic):
        imagelist = glob.glob('Quiz/sdvximage/*')
        imagelist = [_.replace('Quiz/sdvximage/','').replace('.jpg','').replace('.png','') for _ in imagelist]
        for song in imagelist:
            try:
                del songdic[song]
            except KeyError:
                continue
        return songdic

    async def dl_sdvximage(self, ctx, level):
        url = f'https://www.sdvx.in/sort/sort_{level}.htm'
        html1 = requests.get(url)
        soup = BeautifulSoup(html1.content, "html.parser")
        elms = soup.find_all('script')
        link_list = [elm.get('src') for elm in elms if elm.get('src') != None]
        del link_list[:1]
        songlist = [_.next_sibling.next_sibling for _ in elms if _.next_sibling.next_sibling != '\n' and _.next_sibling.next_sibling != None and '<script' not in str(_.next_sibling.next_sibling)]
        songdict = dict(zip(songlist,link_list))
        newsongdict = self.get_diff_sdvx(songdict)
        difflist = ['m','v','e','g','i','h','a','n']
        dlmsg = await ctx.send('Downloading... 0% done')
        len_songs = len(newsongdict)
        count = 0
        for k,v in newsongdict.items():
            await asyncio.sleep(2)
            for d in difflist:
                try:
                    print(k,v)
                    await asyncio.sleep(1)
                    songname = html.unescape(k)
                    imgurl = 'https://www.sdvx.in' + v[:-3].replace('/js','/jacket').replace('sort', d) + '.png'
                    imgpath = f'Quiz/sdvximage/{self.convert_half_letter(songname)}.png'
                    self.download_file(imgurl, imgpath)
                    break
                except urllib.error.HTTPError as e:
                    print(d)
            count += 1
            progress_per = int(count/len_songs*100)
            await dlmsg.edit(content=f'Downloading... {progress_per}% done')
        await dlmsg.edit(content=f'Downloading... 100% done')

    async def dl_arcaeaimage(self, ctx):
        new_song = self.get_diff('arcaea')
        dlmsg = await ctx.send('Downloading... 0% done')
        len_songs = len(new_song)
        count = 0
        for _ in new_song:
            url = 'https://wikiwiki.jp/arcaea/'+urllib.parse.quote(_)
            await asyncio.sleep(1)
            html = requests.get(url)
            soup = BeautifulSoup(html.content, "html.parser")
            elms = soup.find(src = re.compile('https://cdn.wikiwiki.jp/to/w/arcaea/' + urllib.parse.quote(_)))
            try:
                imgurl = elms.attrs['src']
                imgpath = f'Quiz/arcaeaimage/{self.convert_half_letter(_)}.jpg'
                self.download_file_with_headers(imgurl,imgpath)
                await asyncio.sleep(1)
            except AttributeError:
                await asyncio.sleep(1)
            finally:
                count += 1
                progress_per = int(count/len_songs*100)
                await dlmsg.edit(content=f'Downloading... {progress_per}% done')
        await dlmsg.edit(content=f'Downloading... 100% done')

    async def dl_deemoimage(self, ctx):
        def replace_wiki_exception(text: str) -> str:
            if "Sonatina" in text:
                text = text.replace("Sonatina for", "Sonata for")
            elif "Aquarelle" in _:
                text = text.replace("Aquarelle: 010", "Cigarette (DEEMO ver)")
            elif "&" in text:
                text = text.replace("&", "and")
            elif '"' in text:
                text = text.replace('"', "'")
            return text
        new_song = self.get_diff('deemo')
        dlmsg = await ctx.send('Downloading... 0% done')
        count = 0
        len_songs = len(new_song)
        for _ in new_song:
            _ = _.replace('(Hard)','').replace('(Extra)','')
            _ = replace_wiki_exception(_)
            url = 'https://wikiwiki.jp/deemo/'+urllib.parse.quote(_.replace(":","."))
            await asyncio.sleep(1)
            html = requests.get(url)
            soup = BeautifulSoup(html.content, "html.parser")
            print(url)
            elms = soup.find(src = re.compile('https://cdn.wikiwiki.jp/to/w/deemo/'))
            print(elms)
            
            try:
                imgurl = elms.attrs['src']
                imgpath = f'Quiz/deemoimage/{self.convert_half_letter(_)}.jpg'
                self.download_file_with_headers(imgurl,imgpath)
                await asyncio.sleep(1)
            except AttributeError as e:
                print(e)
                await asyncio.sleep(1)
                try:
                    url = url.replace("DEEMO", "Deemo").replace("Ver.", "ver.")
                    html = requests.get(url)
                    soup = BeautifulSoup(html.content, "html.parser")
                    print(url)
                    elms = soup.find(src = re.compile('https://cdn.wikiwiki.jp/to/w/deemo/'))
                    print(elms)
                    imgurl = elms.attrs['src']
                    imgpath = f'Quiz/deemoimage/{self.convert_half_letter(_)}.jpg'
                    self.download_file_with_headers(imgurl,imgpath)
                    await asyncio.sleep(1)
                except AttributeError as e:
                    print(e)
                    await asyncio.sleep(1)
            finally:
                count += 1
                progress_per = int(count/len_songs*100)
                await dlmsg.edit(content=f'Downloading... {progress_per}% done')
        await dlmsg.edit(content=f'Downloading... 100% done')



        

async def setup(bot: Bot):
    await bot.add_cog(Downloader(bot))
    