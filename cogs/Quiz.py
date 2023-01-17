# -*- coding: utf-8 -*-

import asyncio
import glob
import json
import os
import random
import tempfile

import discord
from discord import Embed, Message
from discord.ext import commands
from discord.ext.commands import Bot, Context
from PIL import Image

from MusicGameBot import AU_ID


class Quiz(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.skip = False

    @commands.command()
    async def quiz(self, ctx: Context, *args):
        """
        Make a quiz and return the name of a person answered the quiz correctly.

        Parameters
        ---------
        *args: str | tuple
            Normally tuple of models.
            Receive a tuple when used in game().
        """
        if len(args) > 0:
            if type(args[0]) is tuple:  # game()からタプルを受け取ると((model))みたいに二重になる
                args = args[0]
        author = await self.send_quiz(ctx, args)
        return author

    async def send_quiz(self, ctx: Context, args: tuple):
        """
        Choose a song randonly and send the quiz.

        Parameters:
        ---------
        args: tuple
            tuple of models
        """

        quizset = {"arcaea", "sdvx", "deemo", "cytus", "chunithm"}
        common = quizset & set(args)
        if len(common) == 0:
            jacketpath_list = self.get_imagepath_list(quizset)
        else:
            jacketpath_list = self.get_imagepath_list(common)
        quizsong_path = random.choice(jacketpath_list)
        crop_size = self.read_qmode(ctx)
        quizsong_name = self.get_songname(quizsong_path)
        await self.send_crop_image(ctx, quizsong_path, crop_size)

        def check(m: Message):
            return (
                (m.content == quizsong_name or m.content == "!skip")
                and m.channel == ctx.channel
                and m.reference != None
                and self.skip == False
            )

        try:
            msg: Message = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            if ctx.guild.id == AU_ID:
                await ctx.send("<:zako:832420177315758091>")
            await ctx.send(
                f'答え: "{quizsong_name}" やで', file=discord.File(quizsong_path)
            )

        else:
            if msg.content == "!skip":
                await ctx.send(
                    f'答え: "{quizsong_name}" やで', file=discord.File(quizsong_path)
                )
            else:
                await msg.reply("正解です。おめでとう！", file=discord.File(quizsong_path))
                return msg.author

    def get_imagepath_list(self, models: set) -> list:
        """Get the directories of all songs of the designated models, and return that list."""

        imagepath_list = []
        for _ in models:
            imagepath_list += glob.glob(f"Quiz/{_}image/*")
        return imagepath_list

    def get_songname(self, quizsong_path: str) -> str:
        """Remove the extra directory name and the extension, and return the name of song."""

        reversed_songpath = quizsong_path[::-1]
        songname = ""
        for _ in reversed_songpath:
            if _ == "/":
                break
            songname += _
        songname = songname[::-1]
        songname = songname.replace(".png", "").replace(".jpg", "")
        return songname

    async def send_crop_image(self, ctx: Context, quizsong_path: str, crop_size=3):
        """
        Crop a image to make a quiz, and send the quiz.

        Parameters
        ---------
        quizsong_path: str
            the directory of a jacket image file
        crop_size: int, default 3
            The higher the number, the smaller the image is cropped.
        """
        im = Image.open(quizsong_path)
        width = im.width
        height = im.height
        width_min = random.randint(0, int(width / crop_size * (crop_size - 1)))
        height_min = random.randint(0, int(height / crop_size * (crop_size - 1)))
        im_crop = im.crop(
            (
                width_min,
                height_min,
                width_min + width / crop_size,
                height_min + height / crop_size,
            )
        )
        tmpdir = tempfile.TemporaryDirectory()
        cropped_path = os.path.join(tmpdir.name, "crop.png")
        im_crop.save(cropped_path, quality=95)
        await ctx.send(
            "ジャケット絵クイズ！\n30秒以内に正式名称をこのメッセージにリプライして答えてください。",
            file=discord.File(cropped_path),
        )
        tmpdir.cleanup()

    def read_qmode(self, ctx: Context) -> int:
        """Read the difficulty of the quiz from the json file then return the crop size."""

        with open("Quiz/quizmode.json") as f:
            d = json.load(f)
        diff = "normal"
        for k, v in d.items():
            if int(k) == ctx.guild.id:
                diff = v
                break
        if diff == "hard":
            crop_size = 6
        elif diff == "normal":
            crop_size = 3
        return crop_size

    @commands.command()
    async def quizmode(self, ctx: Context, arg: str):
        """
        Change the difficulty of the quiz for each server.
        The difficulty is saved to the json file.

        Parameters
        ---------
        arg: str
            "normal" or "hard"
        """

        if arg.lower() == "hard":
            quizdiff = "hard"
            await ctx.send("クイズの難易度をhardに設定したで。")
        elif arg.lower() == "normal":
            quizdiff = "normal"
            await ctx.send("クイズの難易度をnormalに設定したで。")
        else:
            return await ctx.send('"!quizmode normal"か"!quizmode hard"の形式で送れや。')
        with open("Quiz/quizmode.json") as f:
            d = json.load(f)
        guild_id = str(ctx.guild.id)
        d[guild_id] = quizdiff
        with open("Quiz/quizmode.json", "w") as f:
            json.dump(d, f, ensure_ascii=False)

    @commands.command()
    async def game(self, ctx: Context, *args: str):
        """
        Make successive quizes and send ranking when the game finishes.

        Parameters
        ---------
        *args: str
            (param1, param2)
            param1: name of model (if any)
            param2: number of quizzes
        """

        resultdic = {}
        times = int(args[-1])
        if times > 101:
            times = 100
        for i in range(times):
            author = await self.quiz(ctx, args[:-1])
            if author is not None:
                try:
                    resultdic[author.name] += 1
                except KeyError:
                    resultdic[author.name] = 1
        sorted_result = sorted(resultdic.items(), key=lambda x: x[1], reverse=True)
        embed = discord.Embed(title="Jacket Quiz")
        if len(sorted_result) <= 0:
            embed = discord.Embed(
                title="Jacket Quiz", description="No one could answer the question."
            )
        else:
            self.set_embed_place(embed, sorted_result)
        embed.set_author(name="Result", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    def set_embed_place(self, embed: Embed, sorted_result: list):
        """Set the ranking to the embed."""

        for i, user in enumerate(sorted_result):
            place = i + 1
            if place == 1:
                embed.add_field(name=f"🥇{place}位🥇", value=f"{user[0]}: {user[1]}pt")
            elif place == 2:
                embed.add_field(name=f"🥈{place}位🥈", value=f"{user[0]}: {user[1]}pt")
            elif place == 3:
                embed.add_field(name=f"🥈{place}位🥈", value=f"{user[0]}: {user[1]}pt")
            else:
                embed.add_field(name=f"{place}位", value=f"{user[0]}: {user[1]}pt")


async def setup(bot):
    await bot.add_cog(Quiz(bot))
