from constants import *
from utilities import *
import discord


async def event_handle_reaction(reaction: discord.RawReactionActionEvent, client: discord.Client, inc=1):
    if reaction.user_id == client.user.id:
        return

    channel = client.get_channel(int(reaction.channel_id))
    if not isinstance(channel, discord.Thread):
        return

    if channel.parent_id not in CHANNELS:
        return

    result = await execute_graphql(
        GRAPHQL_URL,
        GET_THREAD_BY_CONTROLLER,
        {
            "thread_controller_id": str(reaction.message_id)
        },
        GRAPHQL_HEADERS
    )

    if not result:
        return

    threads = result["data"]["thread"]

    if len(threads) == 0:
        return

    thread = threads[0]
    emoji = str(reaction.emoji)
    if emoji not in [POSITIVE_EMOJI, NEGATIVE_EMOJI]:
        return

    if thread["author_id"] == str(reaction.user_id):
        if emoji == POSITIVE_EMOJI:
            is_solved = inc > 0
            await execute_graphql(GRAPHQL_URL,
                                  MARK_THREAD_SOLVED,
                                  {
                                      "thread_id": thread["thread_id"],
                                      "solved": is_solved
                                  },
                                  GRAPHQL_HEADERS
                                  )
            controller = await channel.fetch_message(int(thread["thread_controller_id"]))
            if is_solved:
                await controller.edit(embed=discord.Embed(title=CONTROLLER_TITLE,
                                                          description=SOLVED_MESSAGE,
                                                          color=discord.Color.gold()))
            else:
                await controller.edit(embed=discord.Embed(title=CONTROLLER_TITLE,
                                                          description=UNSOLVED_MESSAGE,
                                                          color=discord.Color.gold()))
    await execute_graphql(GRAPHQL_URL,
                          UPDATE_THREAD_VOTES,
                          {
                              "thread_id": thread["thread_id"],
                              "failed_votes": inc if emoji == NEGATIVE_EMOJI else 0,
                              "solved_votes": inc if emoji == POSITIVE_EMOJI else 0
                          },
                          GRAPHQL_HEADERS)
