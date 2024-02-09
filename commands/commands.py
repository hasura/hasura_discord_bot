from constants import *
from utilities import *
import discord


async def command_commands(interaction: discord.Interaction.response, client: discord.Client):
    await log("List Commands", LOGGING_CHANNEL, client)
    await interaction.response.send_message("TODO: List commands")
