import discord
from database import db_conn
from src import discord_tasks
from src import discord_commands
import variables

# Setup bot perms
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(command_prefix="!", intents=intents)

# Functionality toggles
POLLING_JOB_ENABLED = variables.POLLING_JOB_ENABLED
POST_UPDATES_ENABLED = variables.POST_UPDATES_ENABLED
EMOJI_REPLY_ENABLED = variables.EMOJI_REPLY_ENABLED
MESSAGE_REPLY_ENABLED = variables.MESSAGE_REPLY_ENABLED

# TEST_MODE will only send to stebs place's channel
TEST_MODE_ENABLED = variables.TEST_MODE_ENABLED
STEBS_PLACE_CHANNEL_NAME = variables.STEBS_PLACE_CHANNEL_NAME

# Variables
DISCORD_BOT_TOKEN = variables.DISCORD_BOT_TOKEN

@client.event
async def on_message(message: discord.MessageType):
    
    # exclude warbot so they dont get mad
    if (message.channel.name == 'warbot'):
        return

    # exclude non bot channels so they dont get mad
    if ('bot' not in message.channel.name):
        return

    if message.author == client.user:
        return

    if message.content.startswith("!add "):
        await discord_commands.add_target(message)
        return

    if message.content.startswith("!remove "):
        await discord_commands.remove_target(message)
        return

    if message.content.startswith("!list"):
        await discord_commands.list_targets(message)
        return
    
    if message.content.startswith("!help"):
        await discord_commands.help(message)
        return

    # catchall
    if message.content.startswith("!"):
        await discord_commands.clown(message)
        return

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

    db_conn.db.connect()

    # Start the polling job
    if POLLING_JOB_ENABLED:
        discord_tasks.poll_profile_changes_job.start(client)

client.run(DISCORD_BOT_TOKEN)
