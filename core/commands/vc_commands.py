import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord_slash import SlashCommand, cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from asyncio import sleep
import os
import wave
import contextlib
import math
import shelve

from core.text_to_speech import create_tts_file
from core.utils import timestamp
from core.storage import speaking_messages, embed_contents
from core.preferences import Preferences
import core.defaults


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
                await ctx.send(embed=discord.Embed(
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

    async def _speak(self, ctx, message, is_slash=False):
        if ctx.guild.voice_client is None:
            await ctx.send(embed=discord.Embed(
                title=f":x: I am not in a voice channel.",
                description="Use /join to get me in one!",
                color=discord.Color(8847232)
            ))
            return
        if ctx.author.voice:
            if ctx.author.voice.channel and ctx.author.voice.channel == ctx.guild.voice_client.channel:
                voice_client: discord.voice_client.VoiceClient = ctx.guild.voice_client
                if not voice_client.is_playing():
                    if is_slash:
                        await ctx.defer()

                    core.storage.previous_tts_inputs[ctx.author] = message
                    await self.synthesize_and_speak(ctx, message, voice_client, is_slash)
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

    async def synthesize_and_speak(self, ctx, message, voice_client, is_slash):
        with shelve.open("user_preferences") as db:
            preferences = db.get(f"{ctx.author.id}", Preferences(core.defaults.default_voice_name, core.defaults.default_voice_rate, core.defaults.default_pitch_shift))

        file_path = create_tts_file(self.config["ttsFilePath"], message, preferences)

        with contextlib.closing(wave.open(file_path, "r")) as file:
            frames = file.getnframes()
            rate = file.getframerate()
            duration = frames / float(rate)
        duration_timestamp = timestamp(duration)

        embed_content = message

        speaking_msg = await ctx.send(embed=discord.Embed(
            title=f":speaker: Speaking!",
            description=embed_content,
            color=discord.Color(8847232),
        ).set_footer(text=f"{preferences.voice_name} • {duration_timestamp}"))
        speaking_messages[voice_client] = speaking_msg
        embed_contents[voice_client] = (embed_content, duration_timestamp)

        voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=file_path))

        while voice_client.is_playing() or voice_client.is_paused():
            await sleep(.1)

        await speaking_msg.edit(embed=discord.Embed(
            title=f":speaker: Speaking finished",
            description=embed_content,
            color=discord.Color(8847232)
        ).set_footer(text=f"{preferences.voice_name} • {duration_timestamp}"))

        os.remove(file_path)
        speaking_messages.pop(voice_client)

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
        await self._speak(ctx, text, is_slash=True)

    async def _pause(self, ctx: SlashContext, is_slash=False):
        if ctx.guild.voice_client is None:
            await ctx.send(embed=discord.Embed(
                title=f":x: I am not in a voice channel.",
                description="Use /join to get me in one!",
                color=discord.Color(8847232)
            ))
            return
        if ctx.author.voice:
            if ctx.author.voice.channel and ctx.author.voice.channel == ctx.guild.voice_client.channel:
                voice_client: discord.voice_client.VoiceClient = ctx.guild.voice_client
                if voice_client in speaking_messages.keys():
                    speaking_msg = speaking_messages[voice_client]
                    if voice_client.is_playing():
                        voice_client.pause()
                        await speaking_msg.edit(embed=discord.Embed(
                                title=f":speaker: Speaking (paused)",
                                description=embed_contents[voice_client][0],
                                color=discord.Color(8847232)
                            ).set_footer(text=embed_contents[voice_client][1]))
                        if is_slash:
                            await ctx.send(embed=discord.Embed(
                                title=f":pause_button: Paused",
                                color=discord.Color(8847232)
                            ))
                    else:
                        voice_client.resume()
                        await speaking_msg.edit(embed=discord.Embed(
                            title=f":speaker: Speaking",
                            description=embed_contents[voice_client][0],
                            color=discord.Color(8847232)
                        ).set_footer(text=embed_contents[voice_client][1]))
                        if is_slash:
                            await ctx.send(embed=discord.Embed(
                                title=f":arrow_forward: Unpaused",
                                color=discord.Color(8847232)
                            ))
                else:
                    await ctx.send(embed=discord.Embed(
                        title=f":x: Not speaking anything right now.",
                        color=discord.Color(8847232)
                    ))
                return
        await ctx.send(embed=discord.Embed(
                    title=f":x: You need to be connected to the same voice channel as the bot.",
                    color=discord.Color(8847232)
                ))

    @commands.command(name="pause")
    async def pause(self, ctx):
        await self._pause(ctx)

    @cog_ext.cog_slash(name="pause", description="Pauses or unpauses the currently spoken text")
    async def slashpause(self, ctx):
        await self._pause(ctx, is_slash=True)

    async def _stop(self, ctx):
        if ctx.guild.voice_client is None:
            await ctx.send(embed=discord.Embed(
                title=f":x: I am not in a voice channel.",
                description="Use /join to get me in one!",
                color=discord.Color(8847232)
            ))
            return
        if ctx.author.voice:
            if ctx.author.voice.channel and ctx.author.voice.channel == ctx.guild.voice_client.channel:
                voice_client: discord.voice_client.VoiceClient = ctx.guild.voice_client
                if voice_client in speaking_messages.keys():
                    voice_client.stop()
                    await ctx.send(embed=discord.Embed(
                        title=f":stop_button: Stopped",
                        color=discord.Color(8847232)
                    ))
                else:
                    await ctx.send(embed=discord.Embed(
                        title=f":x: Not speaking anything right now.",
                        color=discord.Color(8847232)
                    ))
                return
        await ctx.send(embed=discord.Embed(
                    title=f":x: You need to be connected to the same voice channel as the bot.",
                    color=discord.Color(8847232)
                ))

    @commands.command(name="stop")
    async def stop(self, ctx):
        await self._stop(ctx)

    @cog_ext.cog_slash(name="stop", description="Stops the currently spoken text")
    async def slashstop(self, ctx):
        await self._stop(ctx)

    async def _repeat(self, ctx, is_slash=False):
        if ctx.guild.voice_client is None:
            await ctx.send(embed=discord.Embed(
                title=f":x: I am not in a voice channel.",
                description="Use /join to get me in one!",
                color=discord.Color(8847232)
            ))
            return
        if ctx.author.voice:
            if ctx.author.voice.channel and ctx.author.voice.channel == ctx.guild.voice_client.channel:
                if ctx.author in core.storage.previous_tts_inputs.keys():
                    voice_client: discord.voice_client.VoiceClient = ctx.guild.voice_client
                    if not voice_client.is_playing():
                        if is_slash:
                            await ctx.defer()

                        await self.synthesize_and_speak(ctx, core.storage.previous_tts_inputs[ctx.author], voice_client, is_slash)
                    else:
                        await ctx.send(embed=discord.Embed(
                            title=f":x: Please wait until I finish speaking.",
                            description="Queue functionality coming soon:tm:",
                            color=discord.Color(8847232)
                        ))
                else:
                    await ctx.send(embed=discord.Embed(
                        title=f":x: Nothing to repeat.",
                        description="Make me say something with /speak first",
                        color=discord.Color(8847232)
                    ))
                return
        await ctx.send(embed=discord.Embed(
            title=f":x: You need to be connected to the same voice channel as the bot.",
            color=discord.Color(8847232)
        ))

    @commands.command(name="repeat")
    async def repeat(self, ctx):
        await self._repeat(ctx)

    @cog_ext.cog_slash(name="repeat", description="Repeats the last thing you made the bot say")
    async def slashrepeat(self, ctx):
        await self._repeat(ctx, is_slash=True)
