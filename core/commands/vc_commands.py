import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from asyncio import sleep
import os

from core.text_to_speech import create_tts_file


class VcCommands(commands.Cog):
    config = None

    def __init__(self, client, config):
        self.client: discord.Client = client
        self.config = config

    async def _join(self, ctx: commands.Context):
        voice_channel: discord.VoiceChannel = ctx.author.voice
        if voice_channel is not None:
            channel = voice_channel.channel
            if self.client.user in channel.members:
                await ctx.send(embed=discord.Embed(
                                    title=f":x: Already connected.",
                                    color=discord.Color(8847232)
                                ))
            elif ctx.guild.voice_client and channel != ctx.guild.voice_client.channel:
                await ctx.send(embed= discord.Embed(
                                    title=f":x: Already connected to another channel.",
                                    color=discord.Color(8847232)
                                ))
            else:
                await channel.connect()

                await ctx.send(embed=discord.Embed(
                                    title=f":white_check_mark: Connected to {channel.name}!",
                                    description=f"Use /speak to make me talk",
                                    color=discord.Color(8847232)
                                ))
        else:
            await ctx.send(embed=discord.Embed(
                            title=f":x: You are not in a voice channel.",
                            description=f"Join a voice channel and then use /join",
                            color=discord.Color(8847232)
                        ))

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
        await ctx.send(embed=discord.Embed(
                    title=f":x: I am not in a voice channel.",
                    description=f"Join a voice channel and then use /join",
                    color=discord.Color(8847232)
                ))

    async def disconnect_from_voice(self, ctx):
        if ctx.author.voice:
            if ctx.author.voice.channel and ctx.author.voice.channel == ctx.guild.voice_client.channel:
                await ctx.guild.voice_client.disconnect()

                await ctx.send(embed=discord.Embed(
                                    title=f":hand_splayed: Disconnected",
                                    color=discord.Color(8847232)
                                ))
                return
        await ctx.send(embed=discord.Embed(
                    title=f":x: You need to be connected to the same voice channel as the bot.",
                    color=discord.Color(8847232)
                ))

    @commands.command(name="leave")
    async def leave(self, ctx):
        await self._leave(ctx)

    @cog_ext.cog_slash(name="leave", description="Leaves the current voice channel")
    async def slashleave(self, ctx):
        await self._leave(ctx)

    async def _speak(self, ctx, message, defer=False):
        if ctx.author.voice:
            if ctx.author.voice.channel and ctx.author.voice.channel == ctx.guild.voice_client.channel:
                voice_client: discord.voice_client.VoiceClient = ctx.guild.voice_client
                if not voice_client.is_playing():
                    if defer:
                        await ctx.defer()

                    await self.synthesize_and_speak(ctx, message, voice_client)
                else:
                    await ctx.send(embed=discord.Embed(
                        title=f":x: Please wait until I finish speaking.",
                        description="Queue functionality coming soon:tm:",
                        color=discord.Color(8847232)
                    ))
                return
        await ctx.send(embed=discord.Embed(
                    title=f":x: You need to be connected to the same voice channel as the bot.",
                    color=discord.Color(8847232)
                ))

    async def synthesize_and_speak(self, ctx, message, voice_client):
        file_path = create_tts_file(self.config["ttsFilePath"], message)

        speaking_msg = await ctx.send(embed=discord.Embed(
            title=f":speaker: Speaking!",
            color=discord.Color(8847232)
        ))

        voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=file_path))

        while voice_client.is_playing():
            await sleep(.1)

        await speaking_msg.edit(embed=discord.Embed(
            title=f":speaker: Speaking finished",
            color=discord.Color(8847232)
        ))

        os.remove(file_path)

    @commands.command(name="speak")
    async def speak(self, ctx):
        message = ctx.message.content.lstrip(f"{self.config['commandPrefix']}speak").strip()
        await self._speak(ctx, message)

    @cog_ext.cog_slash(name="speak", description="Speaks the input text", options=[
        create_option(
            name="text",
            description="The text to speak",
            option_type=3,
            required=True
        )
    ])
    async def slashspeak(self, ctx, text):
        await self._speak(ctx, text, defer=True)
