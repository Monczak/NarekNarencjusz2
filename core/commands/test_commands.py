import discord
from discord.ext import commands
from discord_slash import cog_ext


class TestCommands(commands.Cog):
    guild_ids = []

    def __init__(self, client, guild_ids):
        self.client: discord.Client = client
        self.guild_ids = guild_ids

    async def _ping(self, ctx: commands.Context):
        embed = discord.Embed(
            title=f":ping_pong: Pong!",
            description=f"{round(self.client.latency * 1000)} ms",
            color=discord.Color(8847232)
        )
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        await self._ping(ctx)

    @cog_ext.cog_slash(name="ping", description="Checks the bot's response time", guild_ids=guild_ids)
    async def slashping(self, ctx):
        await self._ping(ctx)

