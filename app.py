from discord.message import Message
from discord.ext import tasks
from discord import app_commands
from constants import *
from utilities import *
from commands.hello import command_hello
from commands.commands import command_commands
from commands.search import command_search
from commands.collections import command_collections
from events.event_on_message import event_on_message
from events.event_handle_reaction import event_handle_reaction
from task_loop.task_loop import execute_task_loop
import discord

# Define which intents we want to use (in this case, messages in guilds)
intents = discord.Intents.default()  # Default intents for basic bot functionalities
intents.messages = True  # Subscribe to messages
intents.message_content = True
intents.guilds = True  # Subscribe to guild events
intents.reactions = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# tree.command is how you create commands

@tree.command(name="hello",
              description="Say hello",
              guild=discord.Object(id=GUILD_ID))
async def hello(interaction: discord.Interaction.response):
    """
    This is a test command. Hello World.
    :param interaction: The incoming interation
    :return: The return from the linked function
    """
    return await command_hello(interaction, client)


@tree.command(name="commands",
              description="List commands",
              guild=discord.Object(id=GUILD_ID))
async def commands(interaction: discord.Interaction.response):
    """
    This command lists the available commands
    :param interaction: The incoming interaction
    :return: The return from the linked function
    """
    return await command_commands(interaction, client)


@tree.command(name="search",
              description="Search our documentation!",
              guild=discord.Object(id=GUILD_ID))
async def search(interaction: discord.Interaction.response, query: str, collection: str, limit: int = 10):
    """
    This command performs a cosine similarity vector search across a collection of embedded documents via an API.

    :param interaction: The incoming interaction
    :param query: The query term to embed and search
    :param collection: The collection represented as an ENUM in the database.
    :param limit: The number of results to return
    :return: The result of the search
    """
    return await command_search(interaction, query, collection, limit)


@tree.command(name="collections",
              description="See which collections are available to search.",
              guild=discord.Object(id=GUILD_ID))
async def collections(interaction: discord.Interaction.response):
    """
    Lists all available collections that can be searched
    :param interaction: The incoming interaction
    :return: The result of the search
    """
    return await command_collections(interaction, client)


@client.event
async def on_ready():
    """
    Occurs when the bot connects or re-connects.
    :return:
    """
    # This could get rate-limited, but since we only are in one Guild (our company guild) I'm not disabling the sync.
    # Disabling this isn't a big deal, once the commands are synced up. We could make a command to sync just as easy.
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    await log(f'The bot has logged in as {client.user}', LOGGING_CHANNEL, client)
    # Only start the task loop if it isn't already running.
    if not task_loop.is_running():
        task_loop.start()


@tasks.loop(seconds=1, count=None, reconnect=True)
async def task_loop():
    """
    The main task loop.

    This is an event loop that runs every 1 second. It runs a transactional mutation to collect any unpublished messages

    If for some reason the task_loop fails, the message won't get sent. This is not a huge deal, the user can ask again.
    That shouldn't happen, however, doing this on a transactional poll like this is useful to ensure no more than
    once delivery, and aim for at least once.
    :return: The linked task loop
    """
    return await execute_task_loop(client)


@client.event
async def on_message(message: Message):
    """
    Each time a message is sent, this fires.

    :param message: The incoming message
    :return: The return from the linked handler function
    """
    return await event_on_message(client, message)


@client.event
async def on_raw_reaction_add(reaction: discord.RawReactionActionEvent):
    """
    This occurs each time a reaction is added. It utilizes the same transaction as a removal, to count the number of
    votes. This will be useful for report generation.

    :param reaction: The incoming reaction
    :return: The response from the linked handler function
    """
    return await event_handle_reaction(reaction, client, 1)


@client.event
async def on_raw_reaction_remove(reaction: discord.RawReactionActionEvent):
    """
    This occurs when a reaction is removed. See on_raw_reaction_add

    :param reaction: The incoming reaction
    :return: The response from the linked handler function
    """
    return await event_handle_reaction(reaction, client, -1)


client.run(CLIENT_SECRET)
