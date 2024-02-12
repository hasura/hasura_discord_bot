from constants import *
from utilities import *
import discord


async def command_commands(interaction: discord.Interaction.response, client: discord.Client):
    embed = discord.Embed(title="Commands Help", description=COMMANDS_MESSAGE)
    await interaction.response.send_message(embed=embed)
