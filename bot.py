import discord
from discord.ext import tasks
from database import db_conn
from datetime import datetime, timedelta
from src import steam_utils
from src import discord_utils
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
POLLING_INTERVAL_SECONDS = variables.POLLING_INTERVAL_SECONDS


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
        await discord_utils.add_target(message)
        return

    if message.content.startswith("!remove "):
        await discord_utils.remove_target(message)
        return

    if message.content.startswith("!list"):
        await discord_utils.list_targets(message)
        return

    # catchall
    if message.content.startswith("!"):
        await discord_utils.clown(message)
        return


@tasks.loop(seconds=POLLING_INTERVAL_SECONDS, count=None)
async def poll_profile_changes_job():
    # load Target and latest alias
    name_update_candidates = []
    status_update_candidates = []

    for currentTarget  in db_conn.get_targets():

        name = currentTarget.name
        steam_id = currentTarget.steam_id
        status = currentTarget.status

        # wget url and pull name
        profile = steam_utils.get_steam_profile(currentTarget)

        newAlias = profile.name
        newStatus = profile.status
        
        print('new status!!! [{}]'.format(newStatus))

        if not newAlias:
            # TODO handle not finding steam name
            print('COULD NOT FIND STEAM NAME!')
            continue

        # update status
        db_conn.updateTargetStatus(steam_id, status)

        # load lastest change and compare
        query = db_conn.getLatestChangeById(steam_id)

        target_url = steam_utils.build_profile_display_url(currentTarget)

        # If no change history, skip comparison and add to update candidates
        if not query:
            db_conn.putChangeRecord(steam_id, newAlias)
            name_update_candidates.append(discord_utils.candidate(name,
                                                                newAlias, '', steam_id, target_url, status))
            continue
        
        previous_alias = query.alias
        
        if newStatus != status:
            db_conn.updateTargetStatus(steam_id, newStatus)
            status_update_candidates.append(discord_utils.candidate(name,
                                                                  newAlias, '', steam_id, target_url, newStatus))

        if previous_alias == newAlias:
            print("we found no name change, skipping")
            continue

        db_conn.putChangeRecord(steam_id, newAlias)
        name_update_candidates.append(discord_utils.candidate(name, newAlias,
                                                            previous_alias, steam_id, target_url, newStatus))

    # if name_update_candidates populated update channels
    if name_update_candidates:
        print("we have name update candidates so we will build the update message")

        msg = discord_utils.build_name_update_message(name_update_candidates)

        channels = discord_utils.get_channel_list(client)

        embedVar = discord.Embed(
            title="Steam Name Changes Detected", color=0xff0000)
        for thing in msg:
            embedVar.add_field(name="", value=thing, inline=False)

        for channel in channels:
            await channel.send(embed=embedVar)
    else:
        print("no name update candidates!")

     # if status_update_candidates populated update channels
    if status_update_candidates:
        print("we have status update candidates so we will build the update message")

        msg = discord_utils.build_status_update_message(status_update_candidates)

        channels = discord_utils.get_channel_list(client)

        embedVar = discord.Embed(
            title="Steam Online Status Changes Detected", color=0xff0000)
        for field_val in msg:
            embedVar.add_field(name="", value=field_val, inline=False)

        for channel in channels:
            await channel.send(embed=embedVar)
    else:
        print("no status update candidates!")

    now = datetime.now()
    next_run_dts = now + timedelta(0, POLLING_INTERVAL_SECONDS)
    print("Polling complete. Next run at {}".format(
        next_run_dts.strftime("%d/%m/%Y %H:%M:%S")))


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

    db_conn.db.connect()

    # Start the polling job
    if POLLING_JOB_ENABLED:
        poll_profile_changes_job.start()

client.run(DISCORD_BOT_TOKEN)
