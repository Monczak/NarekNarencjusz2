import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils import manage_commands

class TestCommands(commands.Cog):
    guild_ids = []
    token = None

    def __init__(self, client, guild_ids, token):
        self.client: discord.Client = client
        self.guild_ids = guild_ids
        self.token = token

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

    @cog_ext.cog_slash(name="ping", description="Checks the bot's response time", guild_ids=[631031037161635861])
    async def slashping(self, ctx):
        await self._ping(ctx)

    @commands.command(name="removecmds")
    async def remove_cmds(self, ctx):
        await manage_commands.remove_all_commands_in(864093985656012811, self.token, 631031037161635861)
        embed = discord.Embed(
            title=f":white_check_mark: All slash commands have been removed",
            color=discord.Color(8847232)
        )
        await ctx.send(embed=embed)
