import os
import json
import glob
import struct

import discord
from discord.ext import commands
from core.logger import Logger
from discord_slash import SlashCommand, ComponentContext
from discord_slash.utils import manage_commands

from core.commands.test_commands import TestCommands
from core.commands.vc_commands import VcCommands
from core.commands.preference_commands import PreferenceCommands
from core.preferences import Preferences

import core.storage
import core.defaults
import tts.sapi


def load_config():
    if os.path.exists("config/config.json"):
        with open("config/config.json", "r") as file:
            config_json = file.read()
        config = json.loads(config_json)
        if os.path.exists("config/secretconfig.json"):
            Logger.log("Using secret config")
            with open("config/secretconfig.json", "r") as file:
                config_json = file.read()
            config.update(json.loads(config_json))
        else:
            Logger.warn("Secret config missing. Features such as local slash commands will not be available.")
        return config
    else:
        Logger.error("No config file found")
        exit(1)


config = load_config()
Logger.log(f"Prefix is {config['commandPrefix']}")

activities = {
    "playing": discord.Game(name=config["activityMessage"]),
    "listening": discord.Activity(type=discord.ActivityType.listening, name=config["activityMessage"]),
    "watching": discord.Activity(type=discord.ActivityType.watching, name=config["activityMessage"]),
    "streaming": discord.Streaming(name=config["activityMessage"], url=""),
    "competing": discord.Activity(type=discord.ActivityType.competing, name=config["activityMessage"]),
}

activity = None
if "activityType" not in config.keys():
    Logger.warn(f"Activity not specified, using blank activity")
elif config["activityType"] not in activities.keys():
    Logger.warn(f"Invalid activity {config['activityType']}, must be one of \"playing\", \"listening\", "
                f"\"watching\", \"streaming\", \"competing\"")
else:
    activity = activities[config["activityType"]]

client = commands.Bot(command_prefix=config["commandPrefix"], activity=activity)
slash = SlashCommand(client, sync_commands=True)

Logger.log("Clearing TTS file folder...")
tts_files = glob.glob(os.path.join(config["ttsFilePath"], "*.wav"))
success = True
for f in tts_files:
    try:
        os.remove(f)
    except OSError as err:
        Logger.error(f"Error while cleaning TTS file folder: {f} : {err.strerror}")
        success = False
if success:
    Logger.log("TTS file folder cleared")
else:
    Logger.warn("TTS file folder still has some files left behind, as some couldn't be removed")

voice = tts.sapi.Sapi()
core.storage.available_voices = voice.get_voice_names()
Logger.log(f"Available voices: {core.storage.available_voices}")

core.defaults.default_voice_name = core.storage.available_voices[0]
core.defaults.default_voice_rate = 0
core.defaults.default_pitch_shift = 0

bitness = struct.calcsize("P") * 8
target = "x64" if bitness > 32 else "x86"
filename = f"libopus-0.{target}.dll"
discord.opus.load_opus(filename)

@client.event
async def on_ready():
    Logger.log(f"Logged in as {client.user.display_name}#{client.user.discriminator}")


def start_bot(token):
    client.add_cog(TestCommands(client, config, token))
    client.add_cog(VcCommands(client, config))
    client.add_cog(PreferenceCommands(client, config))
    client.run(token)
