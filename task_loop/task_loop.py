from utilities import *
from constants import *
import discord


async def execute_task_loop(client: discord.Client):
    """
    This is the main task loop.
    :param client: The discord client. (essentially a singleton)
    :return: None
    """
    # Get all tasks
    result = await execute_graphql(GRAPHQL_URL,
                                   PROCESS_MESSAGES_GRAPHQL,
                                   {},
                                   GRAPHQL_HEADERS)
    # If False result skip as this was a failure.
    if not result:
        return
    # Collect the list of tasks
    all_tasks = result["data"]["update_message"]["returning"]
    for task in all_tasks:
        thread_id = task["thread_id"]
        content = task["content"]
        sources = task["sources"]
        thread = task["thread"]
        thread_controller_id = thread["thread_controller_id"]
        thread_author_id = thread["author_id"]
        channel = client.get_channel(int(thread_id))
        controller = await channel.fetch_message(int(thread_controller_id))
        await send_long_message_in_embeds(channel=channel,
                                          title=RESPONSE_TITLE,
                                          message=content)
        await send_long_message_in_embeds(channel=channel,
                                          title=RESPONSE_SOURCES_TITLE,
                                          message=sources,
                                          color=discord.Color.green())
        help_controller_message = HELP_CONTROLLER_MESSAGE.format(author=thread_author_id,
                                                                 bot=client.user.id,
                                                                 github=GITHUB_LINK)
        controller = await controller.edit(embed=discord.Embed(title=CONTROLLER_TITLE,
                                                               description=help_controller_message,
                                                               color=discord.Color.gold()))
        await controller.add_reaction(POSITIVE_EMOJI)
        await controller.add_reaction(NEGATIVE_EMOJI)
