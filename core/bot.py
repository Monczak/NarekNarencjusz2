import os
import json
from discord.ext import commands
from core.logger import Logger
from discord_slash import SlashCommand

from core.commands.test_commands import TestCommands


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

client = commands.Bot(command_prefix=config["commandPrefix"])
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    Logger.log(f"Logged in as {client.user.display_name}#{client.user.discriminator}")


def start_bot(token):
    client.add_cog(TestCommands(client, config["guildIds"]))
    client.run(token)
