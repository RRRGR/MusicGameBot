# -*- coding: utf-8 -*-

import discord
from discord import Message, PartialEmoji, RawReactionActionEvent, app_commands
from discord.ext import commands
from discord.ext.commands import Bot

from api.api import MusicGameBotAPI
from db.db import MusicGameBotDB
from MusicGameBot import AU_ROLE_ID, OO_ROLE_ID


class Emoji(commands.GroupCog, name="emoji"):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = MusicGameBotDB()
        self.api = MusicGameBotAPI()

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        for emoji in message.guild.emojis:
            if str(emoji.id) in message.content:
                partial_emoji = PartialEmoji.from_str(f"{emoji.name}:{emoji.id}")
                self.db.add_emoji_use(
                    message.guild.id,
                    message.author.id,
                    str(partial_emoji),
                    is_message=True,
                    is_reaction=False,
                )

    def hour_to_year_month_day_hour(self, hour: int) -> tuple[int, int, int, int, int]:
        hours_in_day = 24
        hours_in_week = 7 * hours_in_day
        hours_in_month = 30 * hours_in_day
        hours_in_year = 365 * hours_in_day

        year = hour // hours_in_year
        hour %= hours_in_year
        months = hour // hours_in_month
        hour %= hours_in_month
        week = hour // hours_in_week
        hour %= hours_in_week
        day = hour // hours_in_day
        hour %= hours_in_day

        return year, months, week, day, hour

    def get_hour_from_year_month_week_day_hour(
        self, year: int, month: int, week: int, day: int, hour: int
    ) -> int:
        return (
            (year * 365 * 24) + (month * 30 * 24) + (week * 7 * 24) + (day * 24) + hour
        )

    @app_commands.command()
    @app_commands.describe(year="期間を設定しないと1ヶ月になります")
    async def usage_rank(
        self,
        interaction: discord.Interaction,
        year: int = 0,
        month: int = 0,
        week: int = 0,
        day: int = 0,
        hour: int = 0,
        me: bool = False,
    ):
        "サーバー内で使用頻度の高い絵文字をランキングとして出力"
        await interaction.response.defer()
        hour = self.get_hour_from_year_month_week_day_hour(year, month, week, day, hour)
        hour = None if hour == 0 else hour
        user_id = interaction.user.id if me else None
        result = self.api.get_emoji_count_by_guild_id(
            interaction.guild_id, hour, user_id
        )
        hour = result["hour"]
        year, month, week, day, hour = self.hour_to_year_month_day_hour(hour)
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
        for ranking in result["rankings"]:
            ranking_text += f"{ranking['rank']}. {ranking['PartialEmoji_str']}, {ranking['usage_count']}回\n"
            if len(ranking_text) > 900:
                break
        if len(ranking_text) == 0:
            ranking_text = "No emoji has been used."
        embed.add_field(name="Ranking", value=ranking_text)
        await interaction.followup.send(embed=embed)

    @app_commands.command()
    @app_commands.describe(emoji="指定しないと全絵文字の使用回数を出力します", year="期間を設定しないと1ヶ月になります")
    async def member_rank(
        self,
        interaction: discord.Interaction,
        emoji: str | None,
        year: int = 0,
        month: int = 0,
        week: int = 0,
        day: int = 0,
        hour: int = 0,
    ):
        "絵文字を指定するとその絵文字の使用回数の多い人を出力"
        await interaction.response.defer()
        hour = self.get_hour_from_year_month_week_day_hour(year, month, week, day, hour)
        hour = None if hour == 0 else hour
        result = self.api.get_member_rank(interaction.guild_id, emoji, hour)
        hour = result["hour"]
        year, month, week, day, hour = self.hour_to_year_month_day_hour(hour)
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
        for ranking in result["rankings"]:
            ranking_text += f"{ranking['rank']}. {self.bot.get_user(ranking['user_id'])}, {ranking['usage_count']}回\n"
            if len(ranking_text) > 900:
                break
        if len(ranking_text) == 0:
            ranking_text = "The emoji has not been used."
        field_name = f"Ranking of {emoji}" if emoji else "Ranking"
        embed.add_field(name=field_name, value=ranking_text)
        await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        guild_id = payload.guild_id
        self.db.add_emoji_use(
            guild_id,
            payload.user_id,
            str(payload.emoji),
            is_message=False,
            is_reaction=True,
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
