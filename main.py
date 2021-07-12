import discord
import os

from core.logger import Logger
from core.bot import start_bot

# Check if token is present
if os.path.exists("config/token"):
    with open("config/token", "r") as file:
        token = file.read()
else:
    Logger.error("No token file found, cannot start bot. You need to provide a file "
                 "named \"token\" in the config folder which contains the bot token.")
    exit(1)

Logger.log("Narek Narencjusz 2.0 starting up!")
start_bot(token)
