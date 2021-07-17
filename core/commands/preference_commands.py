import asyncio

import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord_slash import SlashCommand, cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select, create_select_option, wait_for_component
from discord_slash.model import ButtonStyle
from asyncio import sleep, wait_for
import os
import wave
import contextlib
import math
import re
import shelve

import core.storage
import core.defaults
from core.text_to_speech import create_tts_file
from core.utils import timestamp, truncate_with_ellipsis
from core.preferences import Preferences


class PreferenceCommands(commands.Cog):
    config = None

    def __init__(self, client, config):
        self.client: discord.Client = client
        self.config = config

    async def _voice(self, ctx):
        with shelve.open("user_preferences") as db:
            preferences = db.get(f"{ctx.author.id}",
                                 Preferences(core.defaults.default_voice_name, core.defaults.default_voice_rate))

        await ctx.send(embed=discord.Embed(
                        title=f":speaking_head: Your voice preferences",
                        description=f"**{preferences.voice_name}**\n"
                                    f":timer: Speaking rate: {preferences.voice_rate}",
                        color=discord.Color(8847232)
        ).set_footer(text="Use the /voice subcommands to modify these preferences."))

    @cog_ext.cog_subcommand(base="voice", name="show", description="Shows your voice preferences")
    async def slashvoice(self, ctx):
        await self._voice(ctx)

    def clean_voice_name(self, name):
        to_remove = ["Microsoft", "Desktop"]
        return " ".join([word for word in name.split() if word not in to_remove])

    async def _selectvoice(self, ctx):
        voice_list = '\n'.join([f'• {name}' for name in core.storage.available_voices])
        cleaned_names = [self.clean_voice_name(name) for name in core.storage.available_voices]
        options = [create_select_option(truncate_with_ellipsis(cleaned_names[i], 25),
                                        core.storage.available_voices[i])
                   for i in range(len(core.storage.available_voices))]
        action_row = create_actionrow(
                        create_select(
                            options=options,
                            placeholder="Select a voice",
                            min_values=1,
                            max_values=1
                        )
                    )

        msg = await ctx.send(embed=discord.Embed(
            title=":speaking_head: Select a voice!",
            description=f"**Available voices:**\n{voice_list}",
            color=discord.Color(8847232)
        ).set_footer(text="You have 1 minute to select a voice."), components=[action_row])

        try:
            select_ctx: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=60)

            with shelve.open("user_preferences") as db:
                preferences = db.get(f"{select_ctx.author.id}", Preferences(core.defaults.default_voice_name, core.defaults.default_voice_rate))
                preferences.voice_name = select_ctx.selected_options[0]
                db[f"{select_ctx.author.id}"] = preferences

            await select_ctx.edit_origin(embed=discord.Embed(
                                    title=f":speaking_head: You selected {select_ctx.selected_options[0]}.",
                                    color=discord.Color(8847232)), components=None)
        except asyncio.TimeoutError:
            await msg.edit(embed=discord.Embed(
                        title=":x: Timed out",
                        color=discord.Color(8847232)), components=None)

    @cog_ext.cog_subcommand(base="voice", name="select", description="Select a voice of your preference")
    async def slashselectvoice(self, ctx):
        await self._selectvoice(ctx)

    async def _setrate(self, ctx, rate):
        if isinstance(rate, int):
            if -10 <= rate <= 10:
                with shelve.open("user_preferences") as db:
                    preferences = db.get(f"{ctx.author.id}",
                                         Preferences(core.defaults.default_voice_name, core.defaults.default_voice_rate))
                    preferences.voice_rate = rate
                    db[f"{ctx.author.id}"] = preferences

                await ctx.send(embed=discord.Embed(
                    title=f":speaking_head: Voice rate set to {preferences.voice_rate}.",
                    color=discord.Color(8847232)
                ).set_footer(text=f"Using {preferences.voice_name}"))
                return
        await ctx.send(embed=discord.Embed(
                title=f":x: Invalid voice rate.",
                description="Voice rate must be an integer between -10 and 10 (inclusive), where -10 is slowest, "
                            "and 10 is fastest.",
                color=discord.Color(8847232)
        ))

    @commands.command(name="setrate")
    async def setrate(self, ctx):
        rate = int(ctx.message.content.lstrip(f"{self.config['commandPrefix']}setrate").strip())
        await self._setrate(ctx, rate)

    @cog_ext.cog_subcommand(base="voice", name="rate", description="Sets the voice's rate (speaking speed)", options=[
            create_option(
                name="rate",
                description="The voice's rate (integer between -10 and 10)",
                option_type=4,
                required=True,
            )
        ])
    async def slashsetrate(self, ctx, rate):
        await self._setrate(ctx, rate)
