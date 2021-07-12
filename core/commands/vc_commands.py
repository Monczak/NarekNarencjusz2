import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord_slash import cog_ext, SlashContext


class VcCommands(commands.Cog):
    guild_ids = []

    def __init__(self, client, guild_ids):
        self.client: discord.Client = client
        self.guild_ids = guild_ids

    async def _join(self, ctx: commands.Context):
        voice_channel: discord.VoiceChannel = ctx.author.voice
        if voice_channel is not None:
            channel = voice_channel.channel
            if self.client.user in channel.members:
                embed = discord.Embed(
                    title=f":x: Already connected.",
                    color=discord.Color(8847232)
                )
                await ctx.send(embed=embed)
            else:
                await channel.connect()

                embed = discord.Embed(
                    title=f":white_check_mark: Connected to {channel.name}!",
                    description=f"Use /speak to make me talk",
                    color=discord.Color(8847232)
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f":x: You are not in a voice channel.",
                description=f"Join a voice channel and then use /join",
                color=discord.Color(8847232)
            )
            await ctx.send(embed=embed)

    @commands.command(name="join")
    async def join(self, ctx):
        await self._join(ctx)

    @cog_ext.cog_slash(name="join", description="Joins the user's voice channel")
    async def slashjoin(self, ctx):
        await self._join(ctx)

    async def _leave(self, ctx):
        if ctx is commands.Context:
            if ctx.voice_client:
                await self.disconnect_from_voice(ctx)
            else:
                await self.disconnect_not_in_vc(ctx)
        else:
            if ctx.guild.voice_client:
                await self.disconnect_from_voice(ctx)
            else:
                await self.disconnect_not_in_vc(ctx)

    async def disconnect_not_in_vc(self, ctx):
        embed = discord.Embed(
            title=f":x: I am not in a voice channel.",
            description=f"Join a voice channel and then use /join",
            color=discord.Color(8847232)
        )
        await ctx.send(embed=embed)

    async def disconnect_from_voice(self, ctx):
        if ctx.author.voice:
            if ctx.author.voice.channel and ctx.author.voice.channel == ctx.guild.voice_client.channel:
                await ctx.guild.voice_client.disconnect()
                embed = discord.Embed(
                    title=f":hand_splayed: Disconnected",
                    color=discord.Color(8847232)
                )
                await ctx.send(embed=embed)
                return
        embed = discord.Embed(
            title=f":x: You need to be connected to the same voice channel as the bot",
            color=discord.Color(8847232)
        )
        await ctx.send(embed=embed)

    @commands.command(name="leave")
    async def leave(self, ctx):
        await self._leave(ctx)

    @cog_ext.cog_slash(name="leave", description="Leaves the current voice channel")
    async def slashleave(self, ctx):
        await self._leave(ctx)
