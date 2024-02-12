from constants import *
from utilities import *
import discord
from discord.ui import View, Select


# It will be easier to understand if we give users a dropdown.
async def command_collections(interaction: discord.Interaction.response,
                              _: discord.Client):
    if not isinstance(interaction.channel, discord.Thread):
        await interaction.response.send(embed=discord.Embed(title=UNAVAILABLE_COMMAND))
        return

    result = await execute_graphql(
        GRAPHQL_URL,
        GET_DOCS_COLLECTION,
        {},
        GRAPHQL_HEADERS
    )
    documents = [i['value'] for i in result["data"]["COLLECTION_ENUM"]]
    select = Select(placeholder='Searchable Collections', min_values=1, max_values=1)

    # Dynamically add options to the Select component
    for doc in documents:
        select.add_option(label=doc, description="You can use this with the /search command")

    async def select_callback(_interaction: discord.Interaction.response):
        await _interaction.response.send_message(f'You selected {select.values[0]}.', ephemeral=True)

    # Assign the null callback to the select component
    select.callback = select_callback
    # Add more options dynamically as needed
    view = View()
    view.add_item(select)

    await interaction.response.send_message(f"The available document collections are:", view=view, ephemeral=True)
