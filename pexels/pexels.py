import random
import discord
import requests
from redbot.core import Config, commands


class Pexels(commands.Cog):
    """Pexels Image API fetching cog"""

    __version__ = "1.0.0"

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=959327661804448, force_registration=True
        )
        default_global = {
            "pdg": 15,
        }
        default_guild = {
            "pgg": [],
        }
        self.config.register_global(**default_global)
        self.config.init_custom("PexelsGuildGroup", 1)
        self.config.register_custom("PexelsGuildGroup", **default_guild)

    async def pexelscheck(self):
        """Check if the API key is set and get the number set"""
        token = await self.bot.get_shared_api_tokens("pexels")
        return bool(token.get("authorization"))

    @commands.Cog.listener()
    async def get(self, ctx):
        async with ctx.typing():
            if await self.pexelscheck():
                if (
                    await self.config.custom("PexelsGuildGroup", ctx.guild.id).pgg()
                    == []
                ):
                    max_number = await self.config.pdg()
                else:
                    max_number = await self.config.custom(
                        "PexelsGuildGroup", ctx.guild.id
                    ).pgg()
                randomness = random.randint(0, max_number - 1)
                token = await ctx.bot.get_shared_api_tokens("pexels")
                headers = {"Authorization": "{}".format(token["authorization"])}
                r = requests.get(
                    f"https://api.pexels.com/v1/curated?per_page={max_number}",
                    headers=headers,
                )
                data = r.json()
                id = data["photos"][randomness]["id"]
                r = requests.get(
                    f"https://api.pexels.com/v1/photos/{id}?per_page={max_number}",
                    headers=headers,
                )
                data = r.json()
                url = data["src"]["large"]
                return url
            else:
                await ctx.send(
                    "You need to get an API key from https://www.pexels.com/api/"
                )

    @commands.group()
    async def pexels(self, ctx):
        """Options for Pexels cog"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @pexels.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def curated(self, ctx):
        """Send you a random image from pexels.com"""
        if await self.config.custom("PexelsGuildGroup", ctx.guild.id).pgg() == []:
            max_number = await self.config.pdg()
        else:
            max_number = await self.config.custom(
                "PexelsGuildGroup", ctx.guild.id
            ).pgg()
        embed = discord.Embed(
            title="A random picture has appeared",
            color=(await ctx.embed_colour()),
        )
        data = await self.get(ctx)
        embed.set_image(url=data)
        embed.set_footer(
            text=f"Photos provided by Pexels | Results per page {max_number}"
        )
        await ctx.send(embed=embed)

    @commands.guildowner()
    @pexels.command()
    async def number(self, ctx, number: int):
        """Set the number of photos to be fetched from Pexels"""
        if not number:
            return await ctx.send("Enter a number.")
        if number < 15:
            return await ctx.send("The minimum number is 15.")
        if number > 80:
            return await ctx.send("The maximum number is 80.")
        await self.config.custom("PexelsGuildGroup", ctx.guild.id).pgg.set(number)
        await ctx.tick()

    @commands.guildowner()
    @pexels.command()
    async def reset(self, ctx):
        """Resets the guild config of per page results."""
        await self.config.custom("PexelsGuildGroup", ctx.guild.id).pgg.set([])
        await ctx.tick()

    @commands.is_owner()
    @pexels.command()
    async def defnumber(self, ctx, number: int):
        """Set the default number of photos to be fetched from Pexels"""
        if not number:
            return await ctx.send("Enter a number.")
        if number < 15:
            return await ctx.send("The minimum number is 15.")
        if number > 80:
            return await ctx.send("The maximum number is 80.")
        await self.config.pdg.set(number)
        await ctx.tick()
