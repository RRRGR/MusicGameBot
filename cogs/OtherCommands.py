# -*- coding: utf-8 -*-

import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot, Context

from MusicGameBot import AU_ROLE_ID, GG_ID, OO_ID, OO_JOIN_COMMENT, OO_ROLE_ID


class OtherCommands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        if member.guild.id == GG_ID:
            await member.guild.system_channel.send(member.mention)

        if member.guild.id == OO_ID:
            await member.guild.system_channel.send(member.mention + OO_JOIN_COMMENT)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel.id == OO_ROLE_ID:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if str(payload.emoji) == "🔫":
                role = guild.get_role(922736132251353098)
                await member.add_roles(role)
            elif str(payload.emoji) == "<:ac:860494366627856385>":
                role = guild.get_role(922736480999342080)  # Deemo
                await member.add_roles(role)
            elif str(payload.emoji) == "<:pm:860888897902084126>":
                role = guild.get_role(922736571462070273)  # Arcaea
                await member.add_roles(role)
            elif str(payload.emoji) == "<:naki:894564513737736273>":
                role = guild.get_role(945982876032319548)  # プロセカ
                await member.add_roles(role)
            elif str(payload.emoji) == "🎹":
                role = guild.get_role(945983418284527638)  # bms
                await member.add_roles(role)
            elif str(payload.emoji) == "🇴":
                role = guild.get_role(945983567895363604)  # osu
                await member.add_roles(role)
            elif str(payload.emoji) == "<:genshingood:945986301503623208>":
                role = guild.get_role(945983209466900541)  # 原神
                await member.add_roles(role)
            elif str(payload.emoji) == "<:creeper:950415137557344287>":
                role = guild.get_role(950415652005486622)  # マイクラ
                await member.add_roles(role)
            elif str(payload.emoji) == "<:fallguys:991327924848427008>":
                role = guild.get_role(991098471568375889)  # fallguys
                await member.add_roles(role)
            elif str(payload.emoji) == "<:sdvx:1007305409385734304>":
                role = guild.get_role(999984353654362253)  # sdvx
                await member.add_roles(role)
            elif str(payload.emoji) == "<:respect:1007303145279463537>":
                role = guild.get_role(1007307126361837648)  # djmax
                await member.add_roles(role)
            elif str(payload.emoji) == "🚓":
                role = guild.get_role(1007307402091188325)  # malody
                await member.add_roles(role)

        elif channel.id == AU_ROLE_ID:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if str(payload.emoji) == "<:Deemo:909487201186885662>":
                role = guild.get_role(827201207143366657)  # 音ゲー
                await member.add_roles(role)
            elif str(payload.emoji) == "<:parts2:916564761666277436>":
                role = guild.get_role(827200689730093076)  # モンハン
                await member.add_roles(role)
            elif str(payload.emoji) == "🔫":
                role = guild.get_role(839651008200310824)  # Apex
                await member.add_roles(role)
            elif str(payload.emoji) == "<:C_:829691224259821609>":
                role = guild.get_role(846699082638819368)  # マイクラ
                await member.add_roles(role)
            elif str(payload.emoji) == "<:man1:949593139176427520>":
                role = guild.get_role(858720920759697429)  # ウマ娘
                await member.add_roles(role)
            elif str(payload.emoji) == "<:NONKOSDVX:922110899072950322>":
                role = guild.get_role(948208446761730068)  # sdvxエフェクター
                await member.add_roles(role)
            elif str(payload.emoji) == "<:simauma:828634724074389515>":
                role = guild.get_role(920270401567850576)  # 原神
                await member.add_roles(role)
            elif str(payload.emoji) == "<:NONKOMANGEKYO:921986087142981682>":
                role = guild.get_role(951065494826418206)  # ヘキサゴン
                await member.add_roles(role)
            elif str(payload.emoji) == "<:VS:957251241715580948>":
                role = guild.get_role(971027339502829568)  # レディアント
                await member.add_roles(role)
            elif str(payload.emoji) == ":underage:":
                role = guild.get_role(960361568728678470)  # r18
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel.id == OO_ROLE_ID:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if str(payload.emoji) == "🔫":
                role = guild.get_role(922736132251353098)
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:ac:860494366627856385>":
                role = guild.get_role(922736480999342080)
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:pm:860888897902084126>":
                role = guild.get_role(922736571462070273)
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:naki:894564513737736273>":
                role = guild.get_role(945982876032319548)  # プロセカ
                await member.remove_roles(role)
            elif str(payload.emoji) == "🎹":
                role = guild.get_role(945983418284527638)  # bms
                await member.remove_roles(role)
            elif str(payload.emoji) == "🇴":
                role = guild.get_role(945983567895363604)  # osu
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:genshingood:945986301503623208>":
                role = guild.get_role(945983209466900541)  # 原神
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:creeper:950415137557344287>":
                role = guild.get_role(950415652005486622)  # マイクラ
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:fallguys:991327924848427008>":
                role = guild.get_role(991098471568375889)  # fallguys
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:sdvx:1007305409385734304>":
                role = guild.get_role(999984353654362253)  # sdvx
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:respect:1007303145279463537>":
                role = guild.get_role(1007307126361837648)  # djmax
                await member.remove_roles(role)
            elif str(payload.emoji) == "🚓":
                role = guild.get_role(1007307402091188325)  # malody
                await member.remove_roles(role)

        elif channel.id == AU_ROLE_ID:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if str(payload.emoji) == "<:Deemo:909487201186885662>":
                role = guild.get_role(827201207143366657)  # 音ゲー
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:parts2:916564761666277436>":
                role = guild.get_role(827200689730093076)  # モンハン
                await member.remove_roles(role)
            elif str(payload.emoji) == "🔫":
                role = guild.get_role(839651008200310824)  # Apex
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:C_:829691224259821609>":
                role = guild.get_role(846699082638819368)  # マイクラ
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:man1:949593139176427520>":
                role = guild.get_role(858720920759697429)  # ウマ娘
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:NONKOSDVX:922110899072950322>":
                role = guild.get_role(948208446761730068)  # sdvxエフェクター
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:simauma:828634724074389515>":
                role = guild.get_role(920270401567850576)  # 原神
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:NONKOMANGEKYO:921986087142981682>":
                role = guild.get_role(951065494826418206)  # ヘキサゴン
                await member.remove_roles(role)
            elif str(payload.emoji) == "<:VS:957251241715580948>":
                role = guild.get_role(971027339502829568)  # レディアント
                await member.remove_roles(role)
            elif str(payload.emoji) == ":underage:":
                role = guild.get_role(960361568728678470)  # r18
                await member.remove_roles(role)

    @commands.command()
    async def deemocalibration(self, ctx: Context):
        await ctx.send("https://t.co/9VCJfE2lkZ?")

    @commands.command(aliases=["early"])
    async def fast(self, ctx: Context):
        await ctx.send(
            "arcaea:-／Ravon:-／Deemo:-,-／Cytus:-／DJMAX:-／OverRapid:-／dynamix:up arrow(decrease)／d4dj:音ズレ調整-判定調整+／pjsekai:+／malody:chart+, hit-, graphic-／voez:-／TAKUMI³:+"
        )

    @commands.command(aliases=["slow"])
    async def late(self, ctx: Context):
        await ctx.send(
            "arcaea:+／Ravon:+／Deemo:+,+／Cytus:+／DJMAX:+／OverRapid:+／dynamix:down arrow(increase)／d4dj:音ズレ調整+判定調整-／pjsekai:-／malody:chart-, hit+, graphic+／voez:+／TAKUMI³:-"
        )

    @commands.command()
    async def mhelp(self, ctx: Context):
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
