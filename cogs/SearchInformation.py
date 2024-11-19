# -*- coding: utf-8 -*-

import datetime
import os
import discord
from discord import Embed
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context
from typing import List

from api.api import MusicGameBotAPI
from MusicGameBot import PATH_TO_IMAGE


class SearchInformation(commands.GroupCog, name="song"):
    def __init__(self, bot):
        self.bot = bot
        self.api = MusicGameBotAPI()
        super().__init__()

    @app_commands.command()
    @app_commands.describe(title="曲名", game="機種名", artist="作曲者等")
    async def search(
        self,
        interaction: discord.Interaction,
        title: str,
        game: str | None,
        artist: str | None,
    ):
        """Search Songs"""
        await interaction.response.defer()
        result = self.api.search_songs(title, game, artist)
        num_songs = result["total"]
        if num_songs == 0:
            embed = discord.Embed(
                title=title,
                description="No results found.",
                color=discord.Colour.blue(),
            )
            await interaction.followup.send(embed=embed)
        elif num_songs == 1:
            file, embed = make_embed(result["songs"][0])
            await interaction.followup.send(file=file, embed=embed)
        else:
            await interaction.followup.send(
                view=DropdownView(SongsDropdown(result["songs"]))
            )

    @app_commands.command()
    @app_commands.describe(game="機種名", level="レベル (e.g. 20, 14+)")
    async def gacha(
        self,
        interaction: discord.Interaction,
        game: str | None,
        level: str | None,
    ):
        """曲ガチャ"""
        await interaction.response.defer()
        result = self.api.get_random_songs(game, level)
        if result["total"] == 0:
            embed = discord.Embed(
                title="Gacha",
                description="No results found.",
                color=discord.Colour.blue(),
            )
            return await interaction.followup.send(embed=embed)
        file, embed = make_embed(result["songs"][0])
        await interaction.followup.send(file=file, embed=embed)

    @search.autocomplete("game")
    @gacha.autocomplete("game")
    async def game_title_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        game_names = self.api.get_rgdb_game_names()
        return [
            app_commands.Choice(
                name=game_name["game_name"], value=game_name["game_name"]
            )
            for game_name in game_names["game_names"]
            if current.lower() in game_name["game_name"].lower()
        ]


def make_embed(song_data):
    title = song_data["title"]
    artist = song_data["artist"]
    category = song_data["category"]
    image_path = os.path.join(PATH_TO_IMAGE, song_data["jacket_image"])
    length = song_data["length"]
    bpm_main = song_data["bpm_main"]
    bpm_min = song_data["bpm_min"]
    bpm_max = song_data["bpm_max"]
    description = song_data["description"]
    song_url = song_data["song_url"]
    wiki_url = song_data["wiki_url"]
    release_date = song_data["release_date"]
    chart_data = song_data["charts"]
    file = discord.File(image_path, filename="image.jpg")
    embed = discord.Embed(
        title=f"Result: {title}",
        color=discord.Colour.blue(),
        url=wiki_url,
    )
    embed.set_image(url="attachment://image.jpg")
    embed.add_field(name="Artist", value=artist) if artist else None
    embed.add_field(name="Category", value=category) if category else None
    (
        embed.add_field(name="Length", value=datetime.timedelta(seconds=length))
        if length
        else None
    )
    embed.add_field(name="BPM (main)", value=bpm_main) if bpm_main else None
    embed.add_field(name="BPM (min)", value=bpm_min) if bpm_min else None
    embed.add_field(name="BPM (max)", value=bpm_max) if bpm_max else None
    embed.add_field(name="Others", value=description) if description else None
    embed.add_field(name="URL", value=song_url) if song_url else None
    embed.add_field(name="Release", value=release_date) if release_date else None
    for diff in chart_data:
        difficulty_name = diff["difficulty"]
        level = diff["level"]
        const = diff["const"]
        num_notes = diff["num_notes"]
        designer = diff["designer"]
        diff_text = level
        if const:
            diff_text += f" ({const})"
        if num_notes:
            diff_text += f", {num_notes} notes"
        if designer:
            diff_text += f", by {designer}"
        embed.add_field(name=difficulty_name, value=diff_text)
    return file, embed


class SongsDropdown(discord.ui.Select):
    def __init__(
        self,
        song_list: list,
    ):
        self.song_list = song_list
        options = []
        for i, song_data in enumerate(song_list):
            song_title_with_game = f"[{song_data['game_name']}] {song_data['title']} ({song_data['artist']})"
            options.append(
                discord.SelectOption(label=song_title_with_game[:100], value=i)
            )
            if i >= 24:
                break
        super().__init__(
            placeholder="Choose a song from result.",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        api = MusicGameBotAPI()
        selected_index = int(self.values[0])
        selected_song_data = self.song_list[selected_index]
        result = api.search_songs(
            selected_song_data["title"],
            selected_song_data["game_name"],
            selected_song_data["artist"],
        )
        file, embed = make_embed(result["songs"][0])
        await interaction.message.edit(embed=embed, attachments=[file], view=None)


class DropdownView(discord.ui.View):
    def __init__(self, DropdownClass):
        super().__init__()
        self.add_item(DropdownClass)


async def setup(bot: Bot):
    await bot.add_cog(SearchInformation(bot))
