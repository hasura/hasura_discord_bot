# Hasura Discord Bot

This repository contains the code for the Hasura Discord Bot.

The main entrypoint for this application is `app.py`

The project is organized as follows.

Commands for the bot, also known as slash commands are in the `commands` directory.

To run the bot, first copy .env.example into a .env file.

Fill out the details for the .env file with your details:

The Discord client secret to authenticate the bot:
`CLIENT_SECRET=secret`

The API endpoint of the search endpoint:
`SEARCH_ENDPOINT_URL=http://localhost:8100/search/`

The API Header key to send to the API to authenticate:
`SEARCH_ENDPOINT_API_KEY_HEADER=X-API-KEY`

The API key:
`SEARCH_ENDPOINT_API_KEY=secret`

The GraphQL endpoint for GraphQL engine:
`GRAPHQL_URL=https://hasura-bots.hasura.app/v1/graphql`

The Hasura Admin secret:
`GRAPHQL_ADMIN_SECRET=admin_secret`

The Guild the Discord bot should run in:
`GUILD_ID=407792526867693568`

You will need to create your own Discord Application and fill out the details to run this bot.