# -*- coding: utf-8 -*-

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context

from api.api import MusicGameBotAPI
from typing import List


class FriendCode(commands.GroupCog, name="friend_code"):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.api = MusicGameBotAPI()

    @commands.command()
    @commands.is_owner()
    async def friend_code_add_game(self, ctx: Context, game_title: str):
        success = self.api.add_friend_code_game(game_title)
        if success:
            await ctx.send(f"{game_title} has been added.")
        else:
            await ctx.send("Failed.")

    @commands.command()
    @commands.is_owner()
    async def friend_code_delete_game(self, ctx: Context, game_title: str):
        success = self.api.delete_friend_code_game(game_title)
        if success:
            await ctx.send(f"{game_title} has been deleted.")
        else:
            await ctx.send("Failed.")

    @app_commands.command()
    @app_commands.describe(
        game_title="ゲームの名前 available_gameで出てくるタイトル以外入力不可",
        friend_code="フレンドコードを入力",
    )
    async def add(
        self, interaction: discord.Interaction, game_title: str, friend_code: str
    ):
        "フレンドコードを登録"
        await interaction.response.defer()
        success = self.api.upsert_friend_code(
            interaction.user.id, game_title, friend_code
        )
        if success:
            mention = interaction.user.mention
            embed = discord.Embed(title="Friend Code", description=mention)
            embed.add_field(name=game_title, value=friend_code)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Failed.")

    @app_commands.command()
    @app_commands.describe(
        game_title="ゲームの名前 available_gameで出てくるタイトル以外入力不可"
    )
    async def delete(self, interaction: discord.Interaction, game_title: str):
        "ゲームの名前を指定して登録されている自分のフレコを削除"
        await interaction.response.defer()
        success = self.api.delete_friend_code(
            interaction.user.id,
            game_title,
        )
        if success:
            await interaction.followup.send(
                f"Your {game_title} friend code has been deleted."
            )
        else:
            await interaction.followup.send("Failed.")

    @app_commands.command()
    @app_commands.describe(
        member="ユーザーを指定してその人のフレコを出力 指定無しの場合は自分",
        game_title="ゲームの名前 available_gameで出てくるタイトル以外入力不可",
    )
    async def show(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None,
        game_title: str | None,
    ):
        "登録されているフレコを出力"
        await interaction.response.defer()
        if member is None and game_title is None:
            member = interaction.user
        user_id = member.id if member else None
        result = self.api.get_friend_code(user_id, game_title)
        if user_id is not None:
            embed = discord.Embed(
                title="Friend Code",
                description=self.bot.get_user(user_id).mention,
            )
            friend_code_text = ""
            for fc in result["friend_codes"]:
                friend_code_text += f"{fc['game_title']}: {fc['friend_code']}\n"
                if len(friend_code_text) > 900:
                    break
            if len(friend_code_text) == 0:
                friend_code_text = "No friend code has been registered."
            field_name = "Friend Code"
            embed.add_field(name=field_name, value=friend_code_text)

        elif game_title is not None:
            embed = discord.Embed(
                title="Friend Code",
                description=game_title,
            )
            friend_code_text = ""
            for fc in result["friend_codes"]:
                friend_code_text += (
                    f"{self.bot.get_user(fc['user_id']).mention}: {fc['friend_code']}\n"
                )
                if len(friend_code_text) > 900:
                    break
            if len(friend_code_text) == 0:
                friend_code_text = "No friend code has been registered."
            field_name = "Friend Code"
            embed.add_field(name=field_name, value=friend_code_text)
        await interaction.followup.send(embed=embed)

    @app_commands.command()
    @app_commands.describe()
    async def available_games(
        self,
        interaction: discord.Interaction,
    ):
        "扱えるゲームの名前を出力"
        await interaction.response.defer()
        result = self.api.get_game_titles()
        embed = discord.Embed(title="Friend Code", description="Available Game Titles")
        game_titles_text = ""
        for game_title in result["game_titles"]:
            game_titles_text += f"{game_title['game_title']}, "
            if len(game_titles_text) > 900:
                break
        if len(game_titles_text) == 0:
            game_titles_text = "No game has been registered."
        field_name = "Titles"
        embed.add_field(name=field_name, value=game_titles_text)
        await interaction.followup.send(embed=embed)

    @add.autocomplete("game_title")
    @delete.autocomplete("game_title")
    @show.autocomplete("game_title")
    async def game_title_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        game_titles = self.api.get_game_titles()
        return [
            app_commands.Choice(
                name=game_title["game_title"], value=game_title["game_title"]
            )
            for game_title in game_titles["game_titles"]
            if current.lower() in game_title["game_title"].lower()
        ]


async def setup(bot: Bot):
    await bot.add_cog(FriendCode(bot))
