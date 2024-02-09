import aiohttp
from typing import Any
import discord
import asyncio
import random
from constants import LOADING_MESSAGES


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
