from constants import *
from utilities import *
import discord


async def command_hello(interaction: discord.Interaction.response, client: discord.Client):
    await log("Hello command", LOGGING_CHANNEL, client)
    await interaction.response.send_message("Hello World!")
