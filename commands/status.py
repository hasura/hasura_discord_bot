from utilities import *
import discord


async def command_status(interaction: discord.Interaction.response):
    """
    Get the status of a thread.

    :param interaction: The incoming interaction
    :param client: The discord client (a singleton instance of the running bot)
    :return:
    """
    await interaction.response.defer()

    if not isinstance(interaction.channel, discord.Thread):
        await interaction.followup.send(embed=discord.Embed(title=UNAVAILABLE_COMMAND))
        return

    if interaction.channel.parent_id not in CHANNELS:
        await interaction.followup.send(embed=allowed_channels_embed(interaction))
        return

    thread_id = str(interaction.channel.id)
    status_embed = await build_thread_status_embed(thread_id)
    await interaction.followup.send(embed=status_embed)
