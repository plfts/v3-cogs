import discord
from .pexels import Pexels


async def setup(bot):
    cog = Pexels(bot)
    if discord.__version__ == "1.7.3":
        bot.add_cog(cog)
    else:
        await bot.add_cog(cog)
