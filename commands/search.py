from constants import *
import discord
import aiohttp


async def command_search(interaction: discord.Interaction.response, query: str, collection: str, limit: int = 10):
    """
    Performs a vector search across a collection for an embedded query.

    :param interaction: The incoming interaction
    :param query: The query to search for
    :param collection: The name of the collection in Qdrant
    :param limit: The number of results to return, max 100
    :return:
    """
    # Prepare the request payload according to the API's expected schema
    if limit > 100:
        await interaction.response.send_message("The request exceeds the maximum allowed limit of 100 documents.")
        return

    # DEFER the response, the maximum this can take is 15 seconds. That's why it is insufficient for GPT, which needs
    # a task loop but fine for things like a vector search
    await interaction.response.defer()

    payload = {
        "collection": collection,
        "query": query,
        "limit": limit,
        "positive": [],
        "negative": []
    }
    headers = {
        "Content-Type": "application/json",
        SEARCH_ENDPOINT_API_KEY_HEADER: SEARCH_ENDPOINT_API_KEY
    }

    # Make an asynchronous request with aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(SEARCH_ENDPOINT_URL, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()

                # The maximum number of fields in an embed is 25, so chunk the results
                chunks = [data[x:x + 25] for x in range(0, len(data), 25)]

                for chunk in chunks:
                    embed = discord.Embed(title=SEARCH_RESPONSE_EMBED_TITLE, description=query)
                    for link in chunk:
                        rank = link["rank"]
                        url = link["url"]
                        score = link["score"]
                        embed.add_field(name=f"Rank: {rank}", value=f"{url} **Match %{score}**", inline=False)

                    # Send the message back to the Discord channel for each chunk
                    await interaction.followup.send(embed=embed)

            else:
                # This part helps debug the issue by providing server's error details. We are a code server, if there
                # are bugs people might just find it interesting and it'll make it easy to debug. This is public facing
                # anyways
                error_details = await response.text()  # Get the text of the response
                embed = discord.Embed(title="Failed to get search results.", description=error_details)
                await interaction.followup.send(embed=embed)
