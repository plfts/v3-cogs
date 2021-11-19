from .pexels import Pexels

async def setup(bot):
    cog = Pexels(bot)
    bot.add_cog(cog)