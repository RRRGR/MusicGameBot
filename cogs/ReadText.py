# -*- coding: utf-8 -*-

from pydub import AudioSegment, audio_segment
import subprocess
import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, Context
import asyncio
import json
import re
import emoji
from collections import deque
import alkana
from rc.main import en2rome, rome2kana
from MusicGameBot import AU_CHAT_ID, GG_CHAT_ID, OO_CHAT_ID, GC_CHAT_ID, GS_CHAT_ID


class ReadText(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        #self.queue = deque()
        self.queue = {
            AU_CHAT_ID: [],
            GG_CHAT_ID: [],
            OO_CHAT_ID: [],
            GC_CHAT_ID: [],
            GS_CHAT_ID: [],
        }

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        
        if message.guild.voice_client:
            text = message.content
            channel_id = message.channel.id
            if text.startswith('!'):
                pass
            elif (channel_id in self.queue):
                text = self.rmv_unread_and_replace_dic(text, str(message.guild.id))
                if self.judge_en(text) == "en":
                    source = self.creat_enWAV(text)
                else:
                    text = self.replace_dic(text, str(message.guild.id))
                    text = self.convert_en(text)
                    text = text.replace('\n', '')
                    source = self.creat_WAV(text)
                self.play_source(source, message)
                while len(self.queue[channel_id]) > 0:
                    await self.play_queue_source(message)

    
    def play_source(self, source, message: Message, transformed=False, append=True):
        """
        Play a source.
        If the source isn't converted to FFmpegPCMAudio, first convert it.
        If the other source is playing, it is apeended to a queue.
        """
        if transformed:
            source_discord = source
        else:
            source_discord = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source), volume=2)
        try:
            message.guild.voice_client.play(source_discord)
        except discord.errors.ClientException:
            if append:
                self.queue[message.channel.id].append(source_discord)
                #self.queue.append(source_discord)
            else:
                pass

    async def play_queue_source(self, message: Message):
        queue = self.queue
        while message.guild.voice_client.is_playing():
            await asyncio.sleep(1.5)
        self.play_source(queue[message.channel.id].pop(0), message, transformed=True, append=False)

    def creat_WAV(self, text: str) -> str:
        input_file = 'ChatSource/input.txt'
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(text)
        self.run_tts_command(lang="jp")
        mp3file = self.convert_wav_to_mp3('ChatSource/output.wav')
        return mp3file
    
    def creat_enWAV(self, text: str) -> str:
        self.run_tts_command(lang="en", text=text)
        mp3file = self.convert_wav_to_mp3('ChatSource/enoutput.wav')
        return mp3file

    def run_tts_command(self, lang="jp", text=''):
        """If the language is EN, use openjtalk.
        If not, use espeak."""
        if lang == "jp":
            #ローカル
            #open_jtalk = ['open_jtalk']
            #mech = ['-x', '/usr/local/Cellar/open-jtalk/1.11/dic']
            #voice = ['-m', '/usr/local/Cellar/open-jtalk/1.11/voice/mei/mei_normal.htsvoice']
            #speed = ['-r', '1.0']
            #outwav = ['-ow', 'ChatSource/output.wav']
            #inputfile = ['ChatSource/input.txt']

            #OCI
            open_jtalk = ['open_jtalk']
            mech = ['-x', '/var/lib/mecab/dic/open-jtalk/naist-jdic']
            voice = ['-m', '/usr/share/hts-voice/mei/mei_normal.htsvoice']
            speed = ['-r', '1.0']
            outwav = ['-ow', 'ChatSource/output.wav']
            inputfile = ['ChatSource/input.txt']
            cmd = open_jtalk + mech + voice + speed + outwav + inputfile
        elif lang == "en":
            espeak = ['espeak']
            enfile = ['-wChatSource/enoutput.wav']
            entext = [text]
            cmd = espeak + enfile + entext
        subprocess.run(cmd)


    def convert_wav_to_mp3(self, wavfile):
        audio_segment = AudioSegment.from_wav(wavfile)
        mp3file = wavfile.replace('wav', 'mp3')
        audio_segment.export(mp3file, format='mp3')
        return mp3file

    @commands.command()
    async def mjoin(self, ctx: Context):
        if ctx.author.voice is None:
            await ctx.send("自分、ボイスチャンネルおらへんやん！")
            return
        else:
            try:
                await ctx.author.voice.channel.connect()
            except discord.errors.ClientException:
                await ctx.voice_client.disconnect(force=True)
                await ctx.author.voice.channel.connect()

    @commands.command()
    async def mbye(self, ctx: Context):
        if ctx.guild.voice_client is None:
            await ctx.send("接続されてないで。")
            return
        else:
            await ctx.voice_client.disconnect(force=True)

    def rmv_emoji(self, text: str) -> str:
        return ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)

    def rmv_url(self, text: str) -> str:
        """Replace url string to 'url'."""
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        text = re.sub(pattern, 'url', text)
        return text
        
    def find_ineq(self, text: str) -> str:
        """Return the start and end positions of the inequality sign."""
        for _ in range(len(text)):
            if text[_] == '<':
                eqstart = _
            if text[_] == '>':
                eqend = _
                break
        return eqstart, eqend

    def rmv_customemoji(self, text: str) -> str:
        if '<:' in text:
            eqstart, eqend = self.find_ineq(text)
            emojipart = text[eqstart:eqend+1]
            text = text.replace(emojipart,'')
            text = self.rmv_customemoji(text)
        return text

    def rmv_mention(self, text: str) -> str:
        if '<@' in text:
            eqstart, eqend = self.find_ineq(text)
            emojipart = text[eqstart:eqend+1]
            text = text.replace(emojipart,'')
            text = self.rmv_mention(text)
        return text

    def rmv_unread_and_replace_dic(self, text: str, guild_id: str) -> str:
        text = self.rmv_mention(text)
        text = self.rmv_url(text)
        text = self.rmv_customemoji(text)
        text = self.rmv_emoji(text)
        #text = self.replace_dic(text, guild_id)
        return text

    def replace_dic(self, text: str, guild_id: str) -> str:
        """Replace words registerd in the dictionary (json)."""
        text = text.lower()
        with open("ChatSource/dictionary.json") as f:
            dicdata = json.load(f)[guild_id]
        dicdata_sorted = sorted(dicdata, key=len, reverse=True)
        for k in dicdata_sorted:
            k_lower = k.lower()
            if k_lower in text:
                text = text.replace(k_lower, dicdata[k]) 
        return text

    def judge_en(self, text: str) -> str:
        """
        Determine if all letters are alphabetical.

        Returns
        ---------
        'en': if all letters are alphabetical
        'jp': otherwise
        """
        code_regex = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]')
        entext = code_regex.sub('', text)
        entext = entext.replace(' ','').replace('.','').replace(',','').replace('\n','').replace("’","")
        if re.fullmatch('[a-zA-Z0-9]+', entext):
            return "en"
        else:
            return "jp"

    def convert_en(self, text: str) -> str:
        """Replace alphabets in Japanese to hiragana."""
        en_list = re.findall(r"[a-zA-Z]+", text)
        en_list = sorted(en_list, key=len, reverse=True)
        for en in en_list:
            kana = alkana.get_kana(en.lower())
            if kana is None:
                if len(en) > 3:
                    kana = rome2kana(en2rome(en))
                    text = text.replace(en, kana)
            else:
                text = text.replace(en, kana)
        return text


    #実験 アルファベットとそれ以外の文字列を分けて、それぞれespeakとopenjtalkでmp3を作り結合するのを試そうとしてた
    # def split_jpen(text: str) -> list:
    #     jpen_list = []
    #     for i in text:
    #         jp_txt = ''
    #         en_txt = ''
    #         changed = 'jp'
    #         if jp:
    #             jp_txt += i
    #         else:
    #             en_txt += i


                    
async def setup(bot: Bot):
    await bot.add_cog(ReadText(bot))

    

        

    

    
        
        
    
    