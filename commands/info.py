from constants import *
import discord


async def command_info(interaction: discord.Interaction.response):
    embed = discord.Embed(title=INFO_TITLE, description=INFO_MESSAGE.format(github=GITHUB_LINK))
    await interaction.response.send_message(embed=embed)
