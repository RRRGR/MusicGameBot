# -*- coding: utf-8 -*-

import datetime
from typing import Literal

import discord
import gspread
import pandas as pd
from discord import app_commands
from discord.ext import commands
from gspread.worksheet import Worksheet
from oauth2client.service_account import ServiceAccountCredentials

from MusicGameBot import OO_ID, SPREADSHEET_URL

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

json = "spread-sheet-350909-94d641982b67.json"
credentials = ServiceAccountCredentials.from_json_keyfile_name(json, scope)
gc = gspread.authorize(credentials)

apps_list = [
    "Arcaea",
    "プロセカ",
    "バンドリ",
    "Deemo",
    "Cytus",
    "Cytus2",
    "VOEZ",
    "Phigros",
    "Lanota",
    "グルミク(通常)",
    "グルミク(TS)",
    "UNBEATABLE",
    "Rotaeno",
    "Muse Dash",
    "デレステ",
    "BMS",
    "Tone Sphere",
    "OverRapid",
]


@app_commands.guilds(discord.Object(id=OO_ID))
class IR(commands.GroupCog, name="ir"):
    literal_apps = Literal[tuple(apps_list)]
    literal_courses = Literal["ボケ/Master/最頂点/?/★★", "1", "2", "3", "4"]
    literal_directions = Literal["左", "右"]

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command()
    @app_commands.describe(
        app="機種/部門",
        course="コース",
        left_right="スプシ上の課題曲の位置\n一曲しかないコースは左",
        score="換算されたスコア",
        result="リザルト画像\n時間と共に撮影できると良い",
    )
    async def submit(
        self,
        interaction: discord.Interaction,
        app: literal_apps,
        course: literal_courses,
        left_right: literal_directions,
        score: float,
        result: discord.Attachment,
    ):
        """Submit your IR score!"""
        await interaction.response.defer()
        url = result.url
        worksheet = gc.open_by_url(SPREADSHEET_URL).worksheet(app)
        course, course_num, song, diff = self.update_score(
            interaction, app, course, left_right, score, url, worksheet
        )
        if song is None:
            embed = self.error_embed()
        else:
            self.sort_sheet(course_num, worksheet)
            current_rank = self.get_current_rank(
                interaction.user.display_name, course_num, worksheet
            )
            embed = self.submission_embed(
                interaction.user, app, course, song, score, diff, current_rank, url
            )
        await interaction.followup.send(embed=embed)

    def update_score(
        self,
        interaction: discord.Interaction,
        app: str,
        course: str,
        left_right: str,
        score: float,
        url: str,
        worksheet: Worksheet,
    ) -> tuple[str, str, str, str] | tuple[None, None, None, None]:
        author = interaction.user.display_name
        date = interaction.created_at + datetime.timedelta(hours=9)
        date = date.strftime("%Y-%m-%d %H:%M:%S")

        course_num = self.has_course_error(app, course)
        if course_num is None:
            return None, None, None, None

        authcol = 9 * int(course_num) - 6
        for i in range(3, 100):
            cell_author = worksheet.cell(i, authcol).value
            if cell_author is None:
                break
            if cell_author == author:
                break
        row = i

        if left_right == "左":
            worksheet.update_cell(row, authcol, author)
            worksheet.update_cell(row, authcol + 2, score)
            worksheet.update_cell(row, authcol + 4, date)
            worksheet.update_cell(row, authcol + 5, url)

            song = worksheet.cell(2, authcol + 2).value
            max = float(worksheet.cell(1, authcol + 2).value)
        elif left_right == "右":
            worksheet.update_cell(row, authcol, author)
            worksheet.update_cell(row, authcol + 3, score)
            worksheet.update_cell(row, authcol + 4, date)
            worksheet.update_cell(row, authcol + 6, url)

            song = worksheet.cell(2, authcol + 3).value
            max = float(worksheet.cell(1, authcol + 3).value)

        diff = self.get_diff(max, score)

        return course, course_num, song, diff

    def get_diff(self, max: float, score: float) -> str:
        diff = (int(max * 100) - int(float(score) * 100)) / 100
        if diff == 0:
            diff = "MAX"
        elif diff < 0:
            diff = f"MAX+{str(diff*-1)}"
        else:
            diff = f"MAX-{str(diff)}"
        return diff

    def sort_sheet(self, course: str, worksheet: Worksheet) -> None:
        authcol = 9 * int(course) - 6
        if authcol <= 26:
            alphabet_1 = chr(authcol + 64)
        else:
            alphabet_1 = f"A{chr(authcol+64-26)}"
        if authcol <= 20:
            alphabet_2 = chr(authcol + 70)
        elif authcol <= 46:
            alphabet_2 = f"A{chr(authcol+70-26)}"
        else:
            alphabet_2 = f"B{chr(authcol+70-52)}"
        # worksheet.sort((authcol+4,'asc'), range=f'{alphabet_1}3:{alphabet_2}30')
        worksheet.sort((authcol + 1, "des"), range=f"{alphabet_1}3:{alphabet_2}30")

    def submission_embed(
        self,
        user: discord.Member,
        app: str,
        course: str,
        song: str,
        score: float,
        diff: str,
        rank: str,
        img_url: str,
    ) -> discord.Embed:

        embed = discord.Embed(
            title="IR Submission",
            color=0xFF0000,
            description="Your score is registered!",
            url="https://docs.google.com/spreadsheets/d/1AcaH4291rbR4nMzLibisWh5Q5E_h-8Ln2aqvi2NSMRo/edit?usp=sharing",
        )
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.set_image(url=img_url)
        embed.add_field(name="機種/部門", value=app)
        embed.add_field(name="コース", value=course)
        embed.add_field(name="曲", value=song)
        embed.add_field(name="スコア", value=f"{score} ({diff})")
        embed.add_field(name="現在の順位", value=f"{rank}位")
        return embed

    def error_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="IR Submission",
            color=0xFF0000,
            description="An error has occurred.",
            url="https://docs.google.com/spreadsheets/d/1AcaH4291rbR4nMzLibisWh5Q5E_h-8Ln2aqvi2NSMRo/edit?usp=sharing",
        )
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name="Error:", value="機種またはコースの選択に誤りがあります。")
        return embed

    def has_course_error(self, app: str, course: str) -> str | None:
        # コース3, 4を選んだ時のエラー
        if "ボケ" in course:
            pass
        elif app not in ["Arcaea", "プロセカ", "グルミク(通常)", "Muse Dash", "BMS"]:  # コース2まで
            if int(course) >= 3:
                return
        elif app in ["グルミク(通常)", "Muse Dash", "BMS"]:  # コース3まで
            if int(course) >= 4:
                return

        # 特殊コース
        if app in [
            "バンドリ",
            "Deemo",
            "Cytus",
            "Cytus2",
            "Lanota",
            "グルミク(通常)",
            "Rotaeno",
            "デレステ",
            "BMS",
            "Tone Sphere",
        ]:
            if "ボケ" in course:
                course = 1
            else:
                course = int(course) + 1
        elif "ボケ" in course:
            return

        return str(course)

    def get_current_rank(self, author: str, course: str, worksheet: Worksheet) -> int:
        authcol = 9 * int(course) - 6
        for i in range(3, 100):
            cell_author = worksheet.cell(i, authcol).value
            if cell_author is None:
                break
            if cell_author == author:
                break
        row = i
        rank = row - 2
        return rank

    @app_commands.command()
    @app_commands.describe(
        app="機種/部門",
    )
    async def ranking(self, interaction: discord.Interaction, app: literal_apps):
        """Show IR ranking."""
        await interaction.response.defer()
        ranking_embed = self.make_ranking_embed(app)
        await interaction.followup.send(embed=ranking_embed)

    def make_ranking_embed(self, app: str) -> discord.Embed:
        worksheet = gc.open_by_url(SPREADSHEET_URL).worksheet(app)
        ranking_embed = discord.Embed(
            title="IR Current Rankings",
            color=0xFF0000,
            url="https://docs.google.com/spreadsheets/d/1AcaH4291rbR4nMzLibisWh5Q5E_h-8Ln2aqvi2NSMRo/edit?usp=sharing",
            description=app,
        )
        ranking_embed.set_author(
            name=self.bot.user, icon_url=self.bot.user.display_avatar.url
        )
        for i in range(1, 6):
            ranking_embed = self.write_course_ranking(i, ranking_embed, worksheet)
        return ranking_embed

    def write_course_ranking(
        self, coursenum: int, ranking_embed: discord.Embed, worksheet: Worksheet
    ):
        name_col = coursenum * 9 - 6
        try:
            course_name = worksheet.cell(1, name_col - 1).value
        except gspread.exceptions.APIError:  # シートの外側を読み込んだ時
            return ranking_embed
        name_list = worksheet.col_values(name_col)[2:]
        score_col_list = worksheet.col_values(name_col + 1)
        score_list = score_col_list[2:]
        ranking_text = ""
        if len(score_col_list) == 0:
            return ranking_embed
        elif len(name_list) == 0:
            ranking_text = "スコアが登録されていません。"
            ranking_embed.add_field(name=course_name, value=ranking_text, inline=False)
            return ranking_embed
        max = score_col_list[0]
        for i in range(len(name_list)):
            score = score_list[i]
            if i > 0:
                diff = self.get_diff(float(score_memory), float(score))
                if diff == "MAX":
                    ranking_text += f"{i+1}. {name_list[i]}: {score_list[i]} (0)\n"
                else:
                    ranking_text += (
                        f"{i+1}. {name_list[i]}: {score_list[i]} ({diff[3:]})\n"
                    )
            else:
                diff_max = self.get_diff(float(max), float(score))
                ranking_text += f"{i+1}. {name_list[i]}: {score_list[i]} ({diff_max})\n"
            score_memory = score
        ranking_embed.add_field(name=course_name, value=ranking_text, inline=False)
        return ranking_embed


async def setup(bot: commands.Bot):
    await bot.add_cog(IR(bot), guild=discord.Object(id=OO_ID))
