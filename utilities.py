import aiohttp
from typing import Any, Literal
import discord
import asyncio
import random
from constants import *


def get_random_loading_message():
    return random.choice(LOADING_MESSAGES)


def split_content(content, max_length=4096):
    """
    Splits a large string into parts without exceeding the specified maximum length.
    Attempts to split on the last space within the limit to avoid cutting words in half.

    :param content: The string to split.
    :param max_length: The maximum length of each part.
    :return: A list of parts.
    """
    if len(content) <= max_length:
        return [content]

    parts = []
    while content:
        # Check if the content is shorter or equal to the max_length
        if len(content) <= max_length:
            parts.append(content)
            break

        # Find the nearest space to split on to avoid cutting words
        split_index = content.rfind(' ', 0, max_length)
        if split_index == -1:
            # No spaces found, hard split at max_length
            split_index = max_length

        part = content[:split_index].strip()
        parts.append(part)
        content = content[split_index:].strip()

    return parts


async def execute_graphql(url, query, variables, headers) -> Any:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={'query': query, 'variables': variables}, headers=headers) as response:
            if response.status == 200:
                return await response.json()  # Process the JSON response
            else:
                return False


async def log(message: str, channel: int, client: discord.Client):
    await client.get_channel(channel).send(message)


async def send_with_exponential_backoff(channel: discord.Thread, embed: discord.Embed, max_retries=5):
    """
    Attempts to send an embed message to a channel with exponential backoff on rate limit errors.

    :param channel: The Discord channel (or thread) to send the message to.
    :param embed: The Discord Embed object to send.
    :param max_retries: Maximum number of retries before giving up.
    """
    base_delay = 1  # Base delay in seconds, adjust as needed
    attempt = 0

    while attempt < max_retries:
        try:
            response = await channel.send(embed=embed)
            return response
        except discord.HTTPException as e:
            if e.status == 429:  # 429 is the HTTP status code for Too Many Requests (rate limited)
                wait_time = base_delay * 2 ** attempt  # Exponential backoff formula
                print(f"Rate limit hit, attempt {attempt + 1}. Waiting {wait_time} seconds before retrying...")
                await asyncio.sleep(wait_time)
                attempt += 1
            else:
                print(f"HTTPException not related to rate limits: {e}")
                break  # Exit loop for non-rate limit related HTTP exceptions
        except Exception as e:
            print(f"An unexpected error occurred: {e}.")
            break  # Exit loop on unexpected errors
    else:
        # If the loop completes without breaking, all retries have failed or max_retries reached.
        print(f"Failed to send message to {channel} after {max_retries} attempts.")


async def send_long_message_in_embeds(channel: discord.Thread,
                                      title: str,
                                      message: str,
                                      color: discord.Color = discord.Color.blue(),
                                      footer: str | None = None
                                      ):
    chunks = split_content(message)

    if len(chunks) == 0:
        return

    embeds = []
    for chunk in chunks:
        embed = discord.Embed(title=title,
                              description=chunk,
                              color=color)
        embeds.append(embed)
    else:
        if footer:
            embeds[-1].set_footer(text=footer)

    for embed in embeds:
        await send_with_exponential_backoff(channel, embed)


async def send_message_in_embed(channel: discord.Thread,
                                title: str,
                                message: str,
                                color: discord.Color = discord.Color.blue(),
                                ) -> discord.Message:
    embed = discord.Embed(title=title,
                          description=message,
                          color=color)
    return await send_with_exponential_backoff(channel, embed)


async def build_thread_status_embed(thread_id: str) -> discord.Embed:
    response = await execute_graphql(
        GRAPHQL_URL,
        GET_THREAD_FOR_COMMAND,
        {"thread_id": thread_id},
        GRAPHQL_HEADERS
    )

    if not response or 'data' not in response or 'thread_by_pk' not in response['data']:
        return discord.Embed(title="Error", description="Could not fetch thread data.")

    thread = response['data']['thread_by_pk']
    guild_id = GUILD_ID  # Assuming GUILD_ID is defined elsewhere as a constant
    thread_controller_id = thread['thread_controller_id']

    # Construct the message links
    thread_link = f"https://discord.com/channels/{guild_id}/{thread_id}/{thread_id}"
    controller_link = f"https://discord.com/channels/{guild_id}/{thread_id}/{thread_controller_id}"

    # Build the embed
    embed = discord.Embed(title=f"Thread: {thread['title']}", description=f"Thread ID: ```{thread_id}```",
                          color=discord.Color.blue())
    embed.add_field(name="Thread Link", value=f"[Open Thread]({thread_link})", inline=False)
    embed.add_field(name="Controller Message", value=f"[View Controller Message]({controller_link})", inline=False)
    embed.add_field(name="Status", value="Open" if thread['open'] else "Closed", inline=False)
    embed.add_field(name="Solved", value="Yes" if thread['solved'] else "No", inline=False)
    embed.add_field(name=f"{POSITIVE_EMOJI} Votes", value=str(thread['solved_votes']), inline=True)
    embed.add_field(name=f"{NEGATIVE_EMOJI} Votes", value=str(thread['failed_votes']), inline=True)

    return embed


async def allowed_channels_embed(interaction: discord.Interaction.response):
    channels_list = ', '.join([f"<#{channel_id}>" for channel_id in CHANNELS])
    embed = discord.Embed(title=ERROR_MESSAGE_TITLE,
                          description=f"{WRONG_CHANNEL_MESSAGE}{channels_list}",
                          color=discord.Color.gold())
    return await interaction.followup.send(embed=embed)


async def handle_toggle(interaction: discord.Interaction.response,
                        command: Literal["open", "close", "solve", "unsolve"] = "open"):
    await interaction.response.defer()

    if not isinstance(interaction.channel, discord.Thread):
        await interaction.followup.send(embed=discord.Embed(title=UNAVAILABLE_COMMAND))
        return

    if interaction.channel.parent_id not in CHANNELS:
        await interaction.followup.send(embed=allowed_channels_embed(interaction))
        return

    thread_id = str(interaction.channel.id)
    response = await execute_graphql(
        GRAPHQL_URL,
        GET_THREAD_FOR_COMMAND,
        {"thread_id": thread_id},
        GRAPHQL_HEADERS
    )
    thread = response["data"]["thread_by_pk"]
    author_id = thread["author_id"]
    is_open = thread["open"]
    is_solved = thread["solved"]
    user_roles = [role.id for role in interaction.user.roles]

    if str(interaction.user.id) != author_id and MOD_ROLE not in user_roles:
        return await interaction.followup.send(NO_PERMISSION_MESSAGE)

    controller = await interaction.channel.fetch_message(int(thread["thread_controller_id"]))
    help_controller_message = HELP_CONTROLLER_MESSAGE.format(
        author=thread["author_id"],
        bot=interaction.client.user.id,
        github=GITHUB_LINK
    )
    embeds = [
        discord.Embed(title=CONTROLLER_TITLE,
                      description=help_controller_message,
                      color=discord.Color.gold()),
    ]

    if not is_open and command == "open":
        await execute_graphql(GRAPHQL_URL,
                              MARK_THREAD_SOLVED,
                              {
                                  "thread_id": thread_id,
                                  "solved": is_solved,
                                  "open": True
                              },
                              GRAPHQL_HEADERS)
        if interaction.channel.archived:
            await interaction.channel.edit(archived=False)
        if is_solved:
            embeds.append(
                discord.Embed(title=SOLVED_MESSAGE,
                              color=discord.Color.green())
            )
        embeds.append(
            discord.Embed(title=OPENED_MESSAGE,
                          color=discord.Color.yellow())
        )
        await controller.edit(embeds=embeds)
    elif is_open and command == "close":
        await execute_graphql(GRAPHQL_URL,
                              MARK_THREAD_SOLVED,
                              {
                                  "thread_id": thread_id,
                                  "solved": is_solved,
                                  "open": False
                              },
                              GRAPHQL_HEADERS)
        if interaction.channel.archived:
            await interaction.channel.edit(archived=False)
        if is_solved:
            embeds.append(
                discord.Embed(title=SOLVED_MESSAGE,
                              color=discord.Color.green())
            )
        embeds.append(
            discord.Embed(title=CLOSED_MESSAGE,
                          color=discord.Color.red())
        )
        await controller.edit(embeds=embeds)
        if not interaction.channel.archived:
            await interaction.channel.edit(archived=True)
    elif not is_solved and command == "solve":
        await execute_graphql(GRAPHQL_URL,
                              MARK_THREAD_SOLVED,
                              {
                                  "thread_id": thread_id,
                                  "solved": True,
                                  "open": is_open
                              },
                              GRAPHQL_HEADERS)
        re_archive = False
        if interaction.channel.archived:
            re_archive = True
            await interaction.channel.edit(archived=False)
        embeds.append(
            discord.Embed(title=SOLVED_MESSAGE,
                          color=discord.Color.green())
        )
        if re_archive:
            embeds.append(
                discord.Embed(title=CLOSED_MESSAGE,
                              color=discord.Color.red())
            )
        await controller.edit(embeds=embeds)
        if re_archive:
            await interaction.channel.edit(archived=True)
    elif is_solved and command == "unsolve":
        await execute_graphql(GRAPHQL_URL,
                              MARK_THREAD_SOLVED,
                              {
                                  "thread_id": thread_id,
                                  "solved": False,
                                  "open": True
                              },
                              GRAPHQL_HEADERS)
        unarchived = False
        if interaction.channel.archived:
            unarchived = True
            await interaction.channel.edit(archived=False)
        embeds.append(
            discord.Embed(title=UNSOLVED_MESSAGE,
                          color=discord.Color.yellow())
        )
        if unarchived:
            embeds.append(
                discord.Embed(title=OPENED_MESSAGE,
                              color=discord.Color.red())
            )
        await controller.edit(embeds=embeds)

    status_embed = await build_thread_status_embed(thread_id)
    await interaction.followup.send(embed=status_embed)
