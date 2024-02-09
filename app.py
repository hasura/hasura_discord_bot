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


@tree.command(name="hello",
              description="Say hello",
              guild=discord.Object(id=GUILD_ID))
async def hello(interaction: discord.Interaction.response):
    return await command_hello(interaction, client)


@tree.command(name="commands",
              description="List commands",
              guild=discord.Object(id=GUILD_ID))
async def commands(interaction: discord.Interaction.response):
    return await command_commands(interaction, client)


@tree.command(name="search",
              description="Search our documentation!",
              guild=discord.Object(id=GUILD_ID))
async def search(interaction: discord.Interaction.response, query: str, collection: str, limit: int = 10):
    return await command_search(interaction, query, collection, limit)


@tree.command(name="collections",
              description="See which collections are available to search.",
              guild=discord.Object(id=GUILD_ID))
async def collections(interaction: discord.Interaction.response):
    return await command_collections(interaction, client)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    await log(f'The bot has logged in as {client.user}', LOGGING_CHANNEL, client)
    if not task_loop.is_running():
        task_loop.start()


@tasks.loop(seconds=1, count=None, reconnect=True)
async def task_loop():
    return await execute_task_loop(client)


@client.event
async def on_message(message: Message):
    return await event_on_message(client, message)


@client.event
async def on_raw_reaction_add(reaction: discord.RawReactionActionEvent):
    return await event_handle_reaction(reaction, client, 1)


@client.event
async def on_raw_reaction_remove(reaction: discord.RawReactionActionEvent):
    return await event_handle_reaction(reaction, client, -1)


client.run(CLIENT_SECRET)
