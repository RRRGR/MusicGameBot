# -*- coding: utf-8 -*-

import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot, Context

from MusicGameBot import GG_ID, OO_ID, OO_JOIN_COMMENT


class OtherCommands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        if member.guild.id == GG_ID:
            await member.guild.system_channel.send(member.mention)

        if member.guild.id == OO_ID:
            await member.guild.system_channel.send(member.mention + OO_JOIN_COMMENT)

    @commands.hybrid_command()
    async def deemocalibration(self, ctx: Context):
        """Send a spreadsheet link."""
        await ctx.send("https://t.co/9VCJfE2lkZ?")

    @commands.hybrid_command(aliases=["early"])
    async def fast(self, ctx: Context):
        """Show how you should adjust jugdment."""
        await ctx.send(
            "arcaea:-／Ravon:-／Deemo:-,-／Cytus:-／DJMAX:-／OverRapid:-／dynamix:up arrow(decrease)／d4dj:音ズレ調整-判定調整+／pjsekai:+／malody:chart+, hit-, graphic-／voez:-／TAKUMI³:+"
        )

    @commands.hybrid_command(aliases=["slow"])
    async def late(self, ctx: Context):
        """Show how you should adjust jugdment."""
        await ctx.send(
            "arcaea:+／Ravon:+／Deemo:+,+／Cytus:+／DJMAX:+／OverRapid:+／dynamix:down arrow(increase)／d4dj:音ズレ調整+判定調整-／pjsekai:-／malody:chart-, hit+, graphic+／voez:+／TAKUMI³:-"
        )

    @commands.hybrid_command()
    async def mhelp(self, ctx: Context):
        """Show MusicGameBot's commands."""
        embed = discord.Embed(title="コマンド")
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="! + 機種名", value="曲ガチャします\n実装済: !arcaea, !deemo, !sdvx", inline=False
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
        embed.add_field(name="!game [機種] [出題数]", value="quizを連続で出題します。連続MAX100題")
        embed.add_field(
            name="!quizmode + 難易度",
            value="クイズの難易度を指定して画像の切り取られる面積を変更します。難易度指定はhardかnormalのみ",
        )
        embed.add_field(name="!mjoin/!mbye", value="それぞれVCに接続、切断します")
        embed.add_field(name="!addword", value='"コマンド 文字列 読み方"で辞書に読み上げ方を追加します')
        embed.add_field(name="!dltword", value='"コマンド 文字列"で辞書からその文字列の読み上げ方を削除します')
        embed.add_field(
            name="!fast/!late", value="それぞれ早グレと遅グレが出るときの判定の動かす方向を出します", inline=False
        )
        embed.add_field(
            name="!deemocalibration", value="deemoの曲ごとの判定調整の値を出します", inline=False
        )
        await ctx.send(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(OtherCommands(bot))
