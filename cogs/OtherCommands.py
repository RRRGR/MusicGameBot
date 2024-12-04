# -*- coding: utf-8 -*-

import discord
from discord import Member, Message
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import io

from MusicGameBot import GG_ID, OO_ID, OO_JOIN_COMMENT
from api.api import MusicGameBotAPI


class OtherCommands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.api = MusicGameBotAPI()

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        self.api.insert_message_log(
            message.guild.id, message.channel.id, message.author.id
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        if member.guild.id == GG_ID:
            await member.guild.system_channel.send(member.mention)

        if member.guild.id == OO_ID:
            await member.guild.system_channel.send(member.mention + OO_JOIN_COMMENT)

    @app_commands.command(name="best_songs", description="Get a best songs image")
    @app_commands.choices(
        game=[
            app_commands.Choice(name="CHUNITHM", value="chunithm"),
            app_commands.Choice(name="ONGEKI", value="ongeki"),
        ]
    )
    @app_commands.describe(
        game="Game", name_or_id="Chunirec Username/OngekiScoreLog ID"
    )
    async def best_songs(
        self,
        interaction: discord.Interaction,
        game: app_commands.Choice[str],
        name_or_id: str,
    ):
        """Get a best songs image"""
        await interaction.response.defer()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        result_img_src = None
        if game.name == "CHUNITHM":
            driver.get("https://reiwa.f5.si/newbestimg/chunithm/")
            try:
                driver.find_element(By.ID, "chunirec_username").send_keys(name_or_id)
                driver.find_element(By.ID, "generate").click()
                result_img = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "result-img"))
                )
                result_img_src = result_img.get_attribute("src")
            finally:
                driver.quit()
        elif game.name == "ONGEKI":
            driver.get("https://reiwa.f5.si/newbestimg/ongeki/")
            try:
                driver.find_element(By.ID, "osl_id").send_keys(name_or_id)
                driver.find_element(By.ID, "generate").click()

                result_img = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "result-img"))
                )
                result_img_src = result_img.get_attribute("src")
            finally:
                driver.quit()
        if result_img_src:
            header, base64_data = result_img_src.split(",", 1)
            image_data = base64.b64decode(base64_data)
            file = discord.File(io.BytesIO(image_data), filename="image.jpg")
            await interaction.followup.send(file=file)
        else:
            await interaction.followup.send("Counldn't get the image.")

    @commands.hybrid_command()
    async def deemocalibration(self, ctx: Context):
        """Send a spreadsheet link."""
        await ctx.send("https://t.co/9VCJfE2lkZ?")

    @commands.hybrid_command(aliases=["early"])
    async def fast(self, ctx: Context):
        """Show how you should adjust jugdment."""
        embed_1 = discord.Embed(title="判定調整 1/2", description="fast/earlyが出る時")
        embed_1.set_author(
            name=self.bot.user, icon_url=self.bot.user.display_avatar.url
        )
        embed_1.add_field(name="Arcaea", value="-")
        embed_1.add_field(name="ChainBeeT", value="-")
        embed_1.add_field(name="CHUNITHM", value="-/-")
        embed_1.add_field(name="Cytus", value="-")
        embed_1.add_field(name="Deemo", value="-/-")
        embed_1.add_field(name="DDR", value="-")
        embed_1.add_field(name="DJMAX", value="-")
        embed_1.add_field(name="Dynamix", value="↓ (increase)")
        embed_1.add_field(name="D4DJ", value="音ズレ調整:-/判定調整:+")
        embed_1.add_field(name="Hexa Hysteria", value="-")
        embed_1.add_field(name="IIDX", value="+")
        embed_1.add_field(name="KALPA", value="+")
        embed_1.add_field(name="Lanota", value="-")
        embed_1.add_field(name="Lyrica", value="+")
        embed_1.add_field(name="maimai", value="-/-")
        embed_1.add_field(name="Malody", value="chart:+/hit:-/graphic:-")
        embed_1.add_field(name="Malody V", value="-")
        embed_1.add_field(name="MuseDash", value="-")
        embed_1.add_field(name="NOISZ", value="-")
        embed_1.add_field(name="ONGEKI", value="-/-")
        embed_1.add_field(name="Orzmic", value="-")

        embed_2 = discord.Embed(title="判定調整 2/2", description="fast/earlyが出る時")
        embed_2.set_author(
            name=self.bot.user, icon_url=self.bot.user.display_avatar.url
        )
        embed_2.add_field(name="osu!", value="Universal:+/Local:-")
        embed_2.add_field(name="OverRapid", value="-")
        embed_2.add_field(name="Paradigm:Reboot", value="-")
        embed_2.add_field(name="Phigros", value="-")
        embed_2.add_field(name="Polytone", value="-")
        embed_2.add_field(name="RAVON", value="+")
        embed_2.add_field(name="Rizline", value="-")
        embed_2.add_field(name="Rotaeno", value="-")
        embed_2.add_field(name="SDVX", value="+/+")
        embed_2.add_field(name="Sonolus", value="-")
        embed_2.add_field(name="Starri", value="-")
        embed_2.add_field(name="TAKUMI³", value="+")
        embed_2.add_field(name="VOEZ", value="-")
        embed_2.add_field(name="WACCA", value="+")
        embed_2.add_field(name="あんスタ", value="-")
        embed_2.add_field(name="シノスラ", value="+")
        embed_2.add_field(name="ダンカグ", value="+")
        embed_2.add_field(name="グルコス", value="-")
        embed_2.add_field(name="シャニソン", value="+")
        embed_2.add_field(name="プロセカ", value="+")
        embed_2.add_field(name="ユメステ", value="+")
        embed_2.add_field(name="神椿市協奏中", value="+")
        await ctx.send(embeds=[embed_1, embed_2])

    @commands.hybrid_command(aliases=["slow"])
    async def late(self, ctx: Context):
        """Show how you should adjust jugdment."""
        embed_1 = discord.Embed(title="判定調整 1/2", description="late/slowが出る時")
        embed_1.set_author(
            name=self.bot.user, icon_url=self.bot.user.display_avatar.url
        )
        embed_1.add_field(name="Arcaea", value="+")
        embed_1.add_field(name="ChainBeeT", value="+")
        embed_1.add_field(name="CHUNITHM", value="+/+")
        embed_1.add_field(name="Cytus", value="+")
        embed_1.add_field(name="Deemo", value="+/+")
        embed_1.add_field(name="DDR", value="+")
        embed_1.add_field(name="DJMAX", value="+")
        embed_1.add_field(name="Dynamix", value="↑ (decrease)")
        embed_1.add_field(name="D4DJ", value="音ズレ調整:+/判定調整:-")
        embed_1.add_field(name="Hexa Hysteria", value="+")
        embed_1.add_field(name="IIDX", value="-")
        embed_1.add_field(name="KALPA", value="-")
        embed_1.add_field(name="Lanota", value="+")
        embed_1.add_field(name="Lyrica", value="-")
        embed_1.add_field(name="maimai", value="+/+")
        embed_1.add_field(name="Malody", value="chart:-/hit:+/graphic:+")
        embed_1.add_field(name="Malody V", value="+")
        embed_1.add_field(name="MuseDash", value="+")
        embed_1.add_field(name="NOISZ", value="+")
        embed_1.add_field(name="ONGEKI", value="+/+")
        embed_1.add_field(name="Orzmic", value="+")

        embed_2 = discord.Embed(title="判定調整 2/2", description="late/slowが出る時")
        embed_2.set_author(
            name=self.bot.user, icon_url=self.bot.user.display_avatar.url
        )
        embed_2.add_field(name="osu!", value="Universal:-/Local:+")
        embed_2.add_field(name="OverRapid", value="+")
        embed_2.add_field(name="Paradigm:Reboot", value="+")
        embed_2.add_field(name="Phigros", value="+")
        embed_2.add_field(name="Polytone", value="+")
        embed_2.add_field(name="RAVON", value="-")
        embed_2.add_field(name="Rizline", value="+")
        embed_2.add_field(name="Rotaeno", value="+")
        embed_2.add_field(name="SDVX", value="-/-")
        embed_2.add_field(name="Sonolus", value="+")
        embed_2.add_field(name="Starri", value="+")
        embed_2.add_field(name="TAKUMI³", value="-")
        embed_2.add_field(name="VOEZ", value="+")
        embed_2.add_field(name="WACCA", value="-")
        embed_2.add_field(name="あんスタ", value="+")
        embed_2.add_field(name="シノスラ", value="-")
        embed_2.add_field(name="グルコス", value="+")
        embed_2.add_field(name="シャニソン", value="-")
        embed_2.add_field(name="ダンカグ", value="-")
        embed_2.add_field(name="プロセカ", value="-")
        embed_2.add_field(name="ユメステ", value="-")
        embed_2.add_field(name="神椿市協奏中", value="-")
        await ctx.send(embeds=[embed_1, embed_2])

    @app_commands.command(
        name="count", description="Count number of messages in a thread"
    )
    @app_commands.describe(id="Thread ID")
    async def count(
        self,
        interaction: discord.Interaction,
        id: str,
    ):
        """Count number of messages in a thread"""
        await interaction.response.defer()
        try:
            thread = await self.bot.fetch_channel(int(id))
            await interaction.followup.send(thread.message_count)
        except discord.HTTPException as e:
            await interaction.followup.send(f"An error occurred: {e}")

    @commands.hybrid_command()
    async def mhelp(self, ctx: Context):
        """Show MusicGameBot's commands."""
        embed = discord.Embed(title="コマンド")
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="! + 機種名",
            value="曲ガチャします\n実装済: !arcaea, !deemo, !sdvx",
            inline=False,
        )
        embed.add_field(
            name="!sch",
            value="曲検索を行います。!sch ** 機種名 とすると機種を指定できます\n実装済: arcaea, deemo, sdvx",
            inline=False,
        )
        embed.add_field(
            name="!quiz",
            value='音ゲージャケット絵クイズを出題します。"!quiz chunithm" のように機種を指定することもできます(指定しないと全機種から出題)\n実装済: Arcaea, CHUNITHM, Cytus, Deemo, SDVX',
            inline=False,
        )
        embed.add_field(
            name="!game [機種] [出題数]", value="quizを連続で出題します。連続MAX100題"
        )
        embed.add_field(
            name="!quizmode + 難易度",
            value="クイズの難易度を指定して画像の切り取られる面積を変更します。難易度指定はhardかnormalのみ",
        )
        embed.add_field(name="!mjoin/!mbye", value="それぞれVCに接続、切断します")
        embed.add_field(
            name="!addword",
            value='"コマンド 文字列 読み方"で辞書に読み上げ方を追加します',
        )
        embed.add_field(
            name="!dltword",
            value='"コマンド 文字列"で辞書からその文字列の読み上げ方を削除します',
        )
        embed.add_field(
            name="!fast/!late",
            value="それぞれ早グレと遅グレが出るときの判定の動かす方向を出します",
            inline=False,
        )
        embed.add_field(
            name="!deemocalibration",
            value="deemoの曲ごとの判定調整の値を出します",
            inline=False,
        )
        await ctx.send(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(OtherCommands(bot))
