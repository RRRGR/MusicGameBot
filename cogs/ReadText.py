# -*- coding: utf-8 -*-

import asyncio
import re
import subprocess
from collections import deque

import alkana
import discord
import emoji
from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, Context
from pydub import AudioSegment, audio_segment

from db.db import MusicGameBotDB
from MusicGameBot import OPENJTALK_DIC_PATH, OPENJTALK_VOICE_PATH
from rc.main import en2rome, rome2kana


class ReadText(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = MusicGameBotDB()

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.guild.voice_client:
            text = message.content
            channel_id = message.channel.id
            guild_id = message.guild.id
            join_channel = self.db.get_join_channel(guild_id)
            if text.startswith("!"):
                pass
            elif channel_id == join_channel:
                text = self.rmv_unread(text)
                text = text.replace("\n", "")
                await self.play_text(text, message)

    async def play_text(self, text: str | None, message: Message, onfinished=False):
        def on_finished(error):
            text = self.db.get_and_remove_oldest_message(message.guild.id)
            if text is not None:
                asyncio.run_coroutine_threadsafe(
                    self.play_text(text, message, onfinished=True), self.bot.loop
                )

        if text is None:
            text = message.content
        if message.guild.voice_client.is_playing():
            if not onfinished:
                self.db.add_message_to_queue(message.guild.id, text)
                return
        lang = self.judge_en(text)
        if lang == "jp":
            text = self.replace_dic(text, message.guild.id)
            text = self.convert_en(text)
            proc = subprocess.Popen(
                [
                    "open_jtalk",
                    "-x",
                    OPENJTALK_DIC_PATH,
                    "-m",
                    OPENJTALK_VOICE_PATH,
                    "-ow",
                    "/dev/stdout",
                    "-r",
                    "1.0",
                    "-jm",
                    "2.0",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        elif lang == "en":
            proc = subprocess.Popen(
                [
                    "espeak",
                    "-a",
                    "170",
                    "-w",
                    "/dev/stdout",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        proc.stdin.write(text.encode())
        proc.stdin.close()
        audio_source = discord.FFmpegPCMAudio(proc.stdout, pipe=True)
        try:
            message.guild.voice_client.play(audio_source, after=on_finished)
        except discord.errors.ClientException:
            self.db.add_message_to_queue(message.guild.id, text)

    @commands.hybrid_command()
    async def mjoin(self, ctx: Context):
        """Connect to a voice channel where you are."""
        if ctx.author.voice is None:
            await ctx.send("自分、ボイスチャンネルおらへんやん！")
            return
        else:
            try:
                await ctx.author.voice.channel.connect()
                self.db.update_join_channel(ctx.guild.id, ctx.channel.id)
            except discord.errors.ClientException:
                await ctx.voice_client.disconnect(force=True)
                await ctx.author.voice.channel.connect()
                self.db.update_join_channel(ctx.guild.id, ctx.channel.id)

    @commands.hybrid_command()
    async def mbye(self, ctx: Context):
        """Disconnect from a voice channel."""
        if ctx.guild.voice_client is None:
            await ctx.send("接続されてないで。")
            return
        else:
            await ctx.voice_client.disconnect(force=True)

    def rmv_emoji(self, text: str) -> str:
        return emoji.replace_emoji(text)

    def rmv_url(self, text: str) -> str:
        """Replace url string to 'url'."""
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        text = re.sub(pattern, "url", text)
        return text

    def find_ineq(self, text: str) -> str:
        """Return the start and end positions of the inequality sign."""
        for _ in range(len(text)):
            if text[_] == "<":
                eqstart = _
            if text[_] == ">":
                eqend = _
                break
        return eqstart, eqend

    def rmv_customemoji(self, text: str) -> str:
        if "<:" in text:
            eqstart, eqend = self.find_ineq(text)
            emojipart = text[eqstart : eqend + 1]
            text = text.replace(emojipart, "")
            text = self.rmv_customemoji(text)
        return text

    def rmv_mention(self, text: str) -> str:
        if "<@" in text:
            eqstart, eqend = self.find_ineq(text)
            emojipart = text[eqstart : eqend + 1]
            text = text.replace(emojipart, "")
            text = self.rmv_mention(text)
        return text

    def rmv_unread(self, text: str) -> str:
        text = self.rmv_mention(text)
        text = self.rmv_url(text)
        text = self.rmv_customemoji(text)
        text = self.rmv_emoji(text)
        return text

    def replace_dic(self, text: str, guild_id: int) -> str:
        """Replace words registerd in the dictionary (json)."""
        word_list = self.db.get_all_words(guild_id, order_by_length=True)
        for word_tuple in word_list:
            word = word_tuple[0]
            pronunciation = word_tuple[1]
            if word in text:
                text = text.replace(word, pronunciation)
        return text

    def judge_en(self, text: str) -> str:
        """
        Determine if all letters are alphabetical.

        Returns
        ---------
        'en': if all letters are alphabetical
        'jp': otherwise
        """
        code_regex = re.compile(
            "[!\"#$%&'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]"
        )
        entext = code_regex.sub("", text)
        entext = (
            entext.replace(" ", "")
            .replace(".", "")
            .replace(",", "")
            .replace("\n", "")
            .replace("’", "")
        )
        if re.fullmatch("[a-zA-Z0-9]+", entext):
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


async def setup(bot: Bot):
    await bot.add_cog(ReadText(bot))
