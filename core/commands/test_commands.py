import discord
from discord.ext import commands


class TestCommands(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.client.latency * 1000)} ms")
