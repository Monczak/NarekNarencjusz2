from discord.ext import commands
from core.logger import Logger

from core.commands.test_commands import TestCommands

client = commands.Bot(command_prefix="n!")


@client.event
async def on_ready():
    Logger.log(f"Logged in as {client}")


def start_bot(token):
    client.add_cog(TestCommands(client))
    client.run(token)
