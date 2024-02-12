from constants import *
from utilities import *
import discord


async def command_hello(interaction: discord.Interaction.response, client: discord.Client):
    await interaction.response.send_message("Hello World!")
