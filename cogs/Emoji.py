# -*- coding: utf-8 -*-

import discord
from discord import Message, PartialEmoji, RawReactionActionEvent, app_commands
from discord.ext import commands
from discord.ext.commands import Bot

from db.db import MusicGameBotDB
from MusicGameBot import AU_ROLE_ID, OO_ROLE_ID


class Emoji(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = MusicGameBotDB()

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        for emoji in message.guild.emojis:
            if str(emoji.id) in message.content:
                partial_emoji = PartialEmoji.from_str(f"{emoji.name}:{emoji.id}")
                self.db.add_emoji_use(
                    message.guild.id,
                    str(partial_emoji),
                    is_message=True,
                    is_reaction=False,
                )

    @app_commands.command()
    async def emoji_stats(
        self,
        interaction: discord.Interaction,
        year: int = 0,
        month: int = 1,
        week: int = 0,
        day: int = 0,
        hour: int = 0,
    ):
        await interaction.response.defer()
        hour_sum = (
            (year * 365 * 24) + (month * 30 * 24) + (week * 7 * 24) + (day * 24) + hour
        )
        result = self.db.get_emoji_count_by_guild_id(interaction.guild_id, hour_sum)
        interval = ""
        if year != 0:
            interval += f"{year}年"
        if month != 0:
            interval += f"{month}ヶ月"
        if week != 0:
            interval += f"{week}週間"
        if day != 0:
            interval += f"{day}日"
        if hour != 0:
            interval += f"{hour}時間"
        interval += "前"
        embed = discord.Embed(title="絵文字使用状況", description=f"{interval}〜現在まで")
        ranking_text = ""
        counter = 0
        for stats_tuple in result:
            counter += 1
            ranking_text += f"{counter}. {stats_tuple[0]}, {stats_tuple[1]}回\n"
        embed.add_field(name="Ranking", value=ranking_text)
        await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        guild_id = payload.guild_id
        self.db.add_emoji_use(
            guild_id, str(payload.emoji), is_message=False, is_reaction=True
        )

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
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
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


async def setup(bot: Bot):
    await bot.add_cog(Emoji(bot))
