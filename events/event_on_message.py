from constants import *
from utilities import *
import discord


async def event_on_message(client: discord.Client, message: discord.Message):
    """
    Occurs when a message is sent
    :param client: The discord client. (essentially a singleton instance of the bot)
    :param message: The incoming message
    :return: None
    """
    # If the message is from a voice channel, or other weird channel, discard it.
    if not isinstance(message.channel, discord.Thread):
        return

    # If the message is not in the correct channel, discard it.
    if message.channel.parent_id not in CHANNELS:
        return

    # If the bot authored the message, discard it.
    if message.author == client.user:
        return

    thread_id = str(message.channel.id)
    message_id = str(message.id)
    is_new_thread = thread_id == message_id
    bot_mentioned = client.user in message.mentions

    # If it is a new thread, insert into HGE.
    if is_new_thread:
        thread_message = await send_message_in_embed(message.channel,
                                                     title=CONTROLLER_TITLE,
                                                     message=get_random_loading_message(),
                                                     color=discord.Color.gold())
        await execute_graphql(GRAPHQL_URL,
                              INSERT_THREAD_GRAPHQL,
                              {
                                  "object": {
                                      "solved": False,
                                      "open": True,
                                      "thread_id": thread_id,
                                      "title": message.channel.name,
                                      "collection": CHANNELS[message.channel.parent_id],
                                      "thread_controller_id": str(thread_message.id),
                                      "author_id": str(message.author.id)
                                  }
                              },
                              GRAPHQL_HEADERS)
    else:
        pass
    # Insert the message into HGE
    variables = {
        "object": {
            "thread_id": thread_id,
            "message_id": message_id,
            "content": message.content,
            "from_bot": False,
            "first_message": is_new_thread,
            "mentions_bot": bot_mentioned,
            "processed": True
        }
    }
    await execute_graphql(GRAPHQL_URL,
                          INSERT_MESSAGE_GRAPHQL,
                          variables,
                          GRAPHQL_HEADERS)
    if bot_mentioned:
        # Send a message to the user so they know the bot is working on a response.
        await message.channel.send(
            embed=discord.Embed(
                title=get_random_loading_message(),
                color=discord.Color.gold()
            )
        )
