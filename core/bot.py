import os
import json
from discord.ext import commands
from core.logger import Logger

from core.commands.test_commands import TestCommands


def load_config():
    if os.path.exists("config/config.json"):
        with open("config/config.json", "r") as file:
            config_json = file.read()
        config = json.loads(config_json)
        return config
    else:
        Logger.error("No config file found")
        exit(1)


config = load_config()

Logger.log(f"Prefix is {config['commandPrefix']}")

client = commands.Bot(command_prefix=config["commandPrefix"])


@client.event
async def on_ready():
    Logger.log(f"Logged in as {client.user.display_name}#{client.user.discriminator}")


def start_bot(token):
    client.add_cog(TestCommands(client))
    client.run(token)
