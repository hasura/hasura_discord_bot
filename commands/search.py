from constants import *
import discord
import aiohttp


async def command_search(interaction: discord.Interaction.response, query: str, collection: str, limit: int = 10):
    # Prepare the request payload according to the API's expected schema
    if limit > 100:
        await interaction.response.send_message("The request exceeds the maximum allowed limit of 100 documents.")
        return

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

    async with aiohttp.ClientSession() as session:
        async with session.post(SEARCH_ENDPOINT_URL, json=payload, headers=headers) as response:
            if response.status == 200:
                # Assuming the API returns JSON data
                data = await response.json()

                # Initialize variables for pagination
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
                # This part helps debug the issue by providing server's error details
                error_details = await response.text()  # Get the text of the response
                embed = discord.Embed(title="Failed to get search results.", description=error_details)
                await interaction.response.send_message(embed=embed)
