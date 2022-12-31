# -*- coding: utf-8 -*-

from discord.ext import commands
from discord.ext.commands import Bot, Context


class Admin(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(hidden=True)
    async def reload(self, ctx: Context, module: str):
        """A command for reloading files in cogs."""

        await self.bot.reload_extension(module)
        await ctx.send(f"Successfully Reloaded {module}.")


async def setup(bot: Bot):
    await bot.add_cog(Admin(bot))
