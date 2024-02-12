from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

GUILD_ID = 407792526867693568
CHANNELS = {
    1205357708677480468: "v3",  # This is a collection in Qdrant!
    1205630815690817536: "v2"
}
LOGGING_CHANNEL = 1204932258897854504
MOD_ROLE = 407802647412736000
BANNED = []  # NAUGHTY NAUGHTY! BAD USERS!

CLIENT_SECRET = os.getenv('CLIENT_SECRET')

SEARCH_ENDPOINT_URL = os.getenv('SEARCH_ENDPOINT_URL')
SEARCH_ENDPOINT_API_KEY_HEADER = os.getenv('SEARCH_ENDPOINT_API_KEY_HEADER')
SEARCH_ENDPOINT_API_KEY = os.getenv('SEARCH_ENDPOINT_API_KEY')

GRAPHQL_URL = os.getenv('GRAPHQL_URL')
GRAPHQL_ADMIN_SECRET = os.getenv('GRAPHQL_ADMIN_SECRET')
GRAPHQL_HEADERS = {
    "Content-Type": "application/json",
    "x-hasura-admin-secret": GRAPHQL_ADMIN_SECRET
}

INSERT_THREAD_GRAPHQL = """mutation InsertThread($object: thread_insert_input!) {
  insert_thread_one(object: $object) {
    thread_id
    title
    created_at
    updated_at
    open
    solved
    collection
    thread_controller_id
    author_id
  }
}"""

INSERT_MESSAGE_GRAPHQL = """mutation InsertMessage($object: message_insert_input!) {
  insert_message_one(object: $object) {
    thread_id
    message_id
    content
    sources
    from_bot
    first_message
    mentions_bot
    created_at
    updated_at
    processed
  }
}"""

# Check out my nifty transaction. 😎
PROCESS_MESSAGES_GRAPHQL = """mutation ProcessMessages {
  update_message(where: {from_bot: {_eq: true}, processed: {_eq: false}}, _set: {processed: true}) {
    returning {
      content
      created_at
      first_message
      from_bot
      mentions_bot
      message_id
      processed
      sources
      thread_id
      updated_at
      thread {
        thread_controller_id
        author_id
      }
    }
  }
}
"""

GET_THREAD_BY_CONTROLLER = """query GetThreadByControllerId($thread_controller_id: String = "") {
  thread(where: {thread_controller_id: {_eq: $thread_controller_id}}) {
    thread_controller_id
    thread_id
    open
    solved
    author_id
  }
}
"""

GET_THREAD_FOR_COMMAND = """
query ThreadById($thread_id: String = "") {
  thread_by_pk(thread_id: $thread_id) {
    thread_id
    thread_controller_id
    author_id
    title
    open
    solved
    solved_votes
    failed_votes
    collection
    created_at
    updated_at
  }
}
"""

GET_DOCS_COLLECTION = """
query GET_COLLECTIONS_ENUM {
  COLLECTION_ENUM {
    value
  }
}
"""

UPDATE_THREAD_VOTES = """mutation UpdateThreadVotes($thread_id: String = "", $failed_votes: Int = 0, $solved_votes: Int = 0) {
  update_thread_by_pk(pk_columns: {thread_id: $thread_id}, _inc: {failed_votes: $failed_votes, solved_votes: $solved_votes}) {
    thread_id
  }
}
"""

MARK_THREAD_SOLVED = """mutation MarkThreadSolved($thread_id: String = "", $solved: Boolean = false, $open: Boolean = false) {
  update_thread_by_pk(pk_columns: {thread_id: $thread_id}, _set: {solved: $solved, open: $open}) {
    thread_id
  }
}
"""

GITHUB_LINK = "https://github.com/hasura/hasura_discord_show_hn"
HELP_CONTROLLER_MESSAGE = """
<@{author}> can vote on **this message** with a ✅ when this thread has been solved, by the bot or by a human!

Anyone can vote on **this message** with a ❌ if the GPT bot is unhelpful or hallucinating answers.

To continue speaking with the bot, respond in this thread and mention <@{bot}>

**Self-Improving Bot Disclaimer** 
These threads will be used to fine-tune the bot periodically! This is an experiment. 👨‍🔬💻🧪
If you troll the bot, or don't converse constructively to find helpful solutions, it won't learn the answers!
If you do teach it, it'll get wicked smart folks. Be the help you want to receive! The bot learns from how we behave.

Use of this bot is a privilege. It is transparently powered by GPT-4 with RAG performed via Qdrant on our documentation.

Please don't abuse this privilege or we might make it an internal tool only. 
Abusers will be banned from using the bot and publicly shamed. 🤡

This bot is supposed to be helpful! All output from this bot should be trusted at your own risk.

Please read and verify things with the linked documentation.

The source code for this is here: {github}

For a list of available commands the bot can perform, type: ```/commands```
"""

SOLVED_MESSAGE = "This post has been marked as solved!"
UNSOLVED_MESSAGE = "Hmm... At one point this post was marked as solved, but it no longer is. Maybe this is out of date?"
OPENED_MESSAGE = "This post has been re-opened."
CLOSED_MESSAGE = "This post has been closed."

LOADING_MESSAGES = [
    "🤖 Compiling the latest insights for you. 🔄 please wait a second... beep boop",
    "🤖 Tuning in to the data frequencies. 📡 please wait a second... beep boop",
    "🤖 Gathering bytes and bits. 🧲 please wait a second... beep boop",
    "🤖 Calibrating response parameters. 🎛️ please wait a second... beep boop",
    "🤖 Sifting through digital archives. 🗄️ please wait a second... beep boop",
    "🤖 Engaging cognitive circuits. 💡please wait a second... beep boop",
    "🤖 Deciphering the code matrix. 🧬 please wait a second... beep boop",
    "🤖 Navigating through the information maze. 🌐 please wait a second... beep boop",
    "🤖 Assembling the pieces of the puzzle. 🧩 please wait a second... beep boop"
]

POSITIVE_EMOJI = "✅"
NEGATIVE_EMOJI = "❌"
CONTROLLER_TITLE = "Help Bot Thread Information"
RESPONSE_TITLE = "Help Response"
RESPONSE_SOURCES_TITLE = "Help Response Sources"
SEARCH_RESPONSE_EMBED_TITLE = "Search Results"
ERROR_MESSAGE_TITLE = "Error"
WRONG_CHANNEL_MESSAGE = "This command can only be used in the forum channels.\nAllowed Channels: "
NO_PERMISSION_MESSAGE = "You do not have permission to do this on this thread."
COMMANDS_MESSAGE = """
These are all the commands you can use with this bot.

`/hello`
This is a health-check, it should respond with "Hello World!".

`/collections`
This will list the collections available to search. Searching a collection is similar to performing a Google search!

`/search`
The search command takes 2 required parameters and 1 optional parameter.

* query: The query parameter is the search query, this is where you type your question
    
* collection: This is the document collection to search
    
* limit: This optional parameter defaults to 10, but can go up to 100 to return more or less results.


`/solve`
This can be used by a member of the staff to mark a question as being solved. The author of a thread can also vote with a ✅ on the question to mark it as solved.

`/unsolve`
This can be used by a member of the staff to mark a question as being unsolved. Sometimes answers might need updated.

`/close`
This can be used by a member of the staff to close a thread. Either to archive old threads, or for off-topic questions.

`/open`
This can be used by a member of the staff to re-open a closed thread. 

`/status`
This shows the status of the thread it is posted in.
"""
UNAVAILABLE_COMMAND = "This command can only be used in a forum thread."
