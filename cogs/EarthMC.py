import datetime
import time

import requests
from discord.ext import commands
from discord.ext.commands import Bot, Context


class EarthMC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def town(self, ctx: Context, area_limit: int = 100):
        losting_list = get_losting_town()
        for losting_town in losting_list:
            town_data = losting_town[0]
            if town_data["area"] > int(area_limit):
                await ctx.send(
                    f"{losting_town[1]}, area: {town_data['area']}, x: {town_data['x']}, z: {town_data['z']}, name: {town_data['name']}, nation: {town_data['nation']}"
                )


def get_losting_town() -> list:
    players_url = "https://emctoolkit.vercel.app/api/aurora/allplayers"
    players_response = requests.get(players_url)
    players_data = players_response.json()

    towns_url = "https://emctoolkit.vercel.app/api/aurora/towns"
    towns_response = requests.get(towns_url)
    towns_data = towns_response.json()

    losting_list = []
    for town_obj in towns_data:
        if len(town_obj["residents"]) < 2:
            resident_name = town_obj["residents"][0]
            lastOnline = search_player_lastOnline(resident_name, players_data)
            if lastOnline is not None:
                now_unix = int(time.time())
                diff = now_unix - lastOnline
                if diff > 3456000:  # 40 days
                    td = datetime.timedelta(seconds=diff)
                    losting_list.append([town_obj, td])
    return losting_list


def search_player_lastOnline(name, data):
    for d in data:
        if d["name"] == name:
            return d["lastOnline"]


async def setup(bot: Bot):
    await bot.add_cog(EarthMC(bot))
