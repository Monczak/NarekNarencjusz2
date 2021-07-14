import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils import manage_commands
from discord.utils import get
from asyncio import sleep

from core.text_to_speech import create_tts_file


class TestCommands(commands.Cog):
    guild_ids = []
    tts_file_path = ""
    token = None

    def __init__(self, client, config, token):
        self.client: discord.Client = client
        self.guild_ids = config["guildIds"]
        self.tts_file_path = config["ttsFilePath"]
        self.token = token

    async def _ping(self, ctx: commands.Context):
        await ctx.send(embed=discord.Embed(
                    title=f":ping_pong: Pong!",
                    description=f"{round(self.client.latency * 1000)} ms",
                    color=discord.Color(8847232)
                ))

    @commands.command(name="ping")
    async def ping(self, ctx):
        await self._ping(ctx)

    @cog_ext.cog_slash(name="ping", description="Checks the bot's response time")
    async def slashping(self, ctx):
        await self._ping(ctx)

    @commands.command(name="removecmds")
    async def remove_cmds(self, ctx):
        await manage_commands.remove_all_commands_in(864093985656012811, self.token, ctx.guild.id)
        await ctx.send(embed=discord.Embed(
                    title=f":white_check_mark: All slash commands have been removed",
                    color=discord.Color(8847232)
                ))

    async def _testsound(self, ctx: commands.Context):
        voice_client: discord.voice_client.VoiceClient = ctx.guild.voice_client
        await ctx.send("Playback started")
        voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source="etho.ogg"))
        while voice_client.is_playing():
            await sleep(.1)
        await ctx.send("Playback stopped")

    @commands.command(name="testsound")
    async def testsound(self, ctx):
        await self._testsound(ctx)

    async def _testtts(self, ctx: commands.Context, message):
        create_tts_file(self.tts_file_path, message)
        await ctx.send("File created")

    @commands.command(name="testtts")
    async def testtts(self, ctx, message):
        await self._testtts(ctx, message)
