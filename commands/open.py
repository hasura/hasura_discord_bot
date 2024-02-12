from utilities import *
import discord


async def command_open(interaction: discord.Interaction.response):
    """
    Opens the thread if run in a forum channel thread.

    Can only be used by members with the staff role, or the threads author.

    :param interaction: The incoming interaction
    :param client: The discord client (a singleton instance of the running bot)
    :return:
    """
    return await handle_toggle(interaction, "open")
