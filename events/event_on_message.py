from constants import *
from utilities import *
import discord


async def event_on_message(client: discord.Client, message: discord.Message):
    if not isinstance(message.channel, discord.Thread):
        return

    if message.channel.parent_id not in CHANNELS:
        return

    if message.author == client.user:
        return

    thread_id = str(message.channel.id)
    message_id = str(message.id)
    is_new_thread = thread_id == message_id
    bot_mentioned = client.user in message.mentions

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
        await message.channel.send(
            embed=discord.Embed(
                title=get_random_loading_message(),
                color=discord.Color.gold()
            )
        )
