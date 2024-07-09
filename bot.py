import discord
from discord.ext import tasks
import os
import db_conn
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from table2ascii import table2ascii as t2a, PresetStyle
import json

# Setup bot perms
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(command_prefix="!", intents=intents)

# Functionality toggles
POLLING_JOB_ENABLED = True
POST_UPDATES_ENABLED = False
EMOJI_REPLY_ENABLED = False
MESSAGE_REPLY_ENABLED = False
# TEST_MODE will only send to stebs place's channel
TEST_MODE_ENABLED = True

# Variables
DISCORD_BOT_TOKEN = os.environ["BOT_TOKEN"]
STEAM_API_KEY = os.environ["STEAM_API_KEY"]
POLLING_INTERVAL_SECONDS = 30
STEAM_COMMUNITY_TITLE_ERROR = 'Steam Community :: Error'
STEAM_COMMUNITY_PROFILE_URL = 'https://steamcommunity.com/profiles/{}/'
STEAM_COMMUNITY_ID_URL = 'https://steamcommunity.com/id/{}/'
STEAM_API_RESOLVE_VANITY_URL = 'https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}'
HEADER_NAME = '**Name**         |  {}'
HEADER_ALIAS = '**Alias**        |  __**{}**__'
HEADER_NEW_ALIAS = '**New Alias**        |  __**{}**__'
HEADER_STEAM_ID = '**Steam ID**     |  {}'
HEADER_PROFILE_LINK = '**Profile Link** |  {}'


class candidate:
    def __init__(self, name, newAlias, oldAlias, steamId, url):
        self.name = name
        self.newAlias = newAlias
        self.oldAlias = oldAlias
        self.steamId = steamId
        self.url = url


def buildProfileDisplayURL(target: db_conn.Target):
    if target.vanity_url:
        return STEAM_COMMUNITY_ID_URL.format(target.vanity_url)
    else:
        return STEAM_COMMUNITY_PROFILE_URL.format(target.steam_id)


def getSteamNameFromURL(url):
    print("retrieving target steam name")
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    elem = soup.find("title")
    print("raw steam name is: [{}]".format(elem.string))
    if len(elem.string) > 19 and not elem.string == STEAM_COMMUNITY_TITLE_ERROR:
        name = elem.string[19:]
        print("we found the following steam name: [{}]".format(name))
        return name
    else:
        return False


def getSteamIDFromSteamApi(id):
    # TODO handle steam error
    data = requests.get(
        STEAM_API_RESOLVE_VANITY_URL.format(STEAM_API_KEY, id)).json()
    response = data.get("response")
    success = response.get("success")
    steamId = response.get("steamid")
    print('Steam vanity URL response = [{}]'.format(data))
    print('Steam vanity URL success = [{}]'.format(success))
    print('Steam vanity URL steamId = [{}]'.format(steamId))

    if success == 1:
        return steamId
    else:
        return False


def getSteamNameFromSteamId(id):
    print('retrieving target steam name using their Steam ID')
    return getSteamNameFromURL(STEAM_COMMUNITY_PROFILE_URL.format(id))


def getSteamNameFromVanityId(id):
    print('retrieving target steam name using their vanity ID')
    return getSteamNameFromURL(STEAM_COMMUNITY_ID_URL.format(id))


def getChannelList(guilds):
    print("building channel list")

    channels = []

    if TEST_MODE_ENABLED:
        print("TEST_MODE_ENABLED is turned on! building channel list")
        for channel in client.get_all_channels():
            # skip warbot so they dont get mad
            if (channel.name == 'bot_steb'):
                channels.append(channel)
        return channels

    for channel in client.get_all_channels():
        # skip warbot so they dont get mad
        if (channel.name == 'warbot'):
            continue

        if 'bot' in channel.name:
            channels.append(channel)
    return channels


def buildMessage(candidates):
    print("building update message")
    output = []

    for candidate in candidates:
        tableBody = []
        tableBody.append(HEADER_NAME.format(candidate.name))
        tableBody.append(HEADER_NEW_ALIAS.format(candidate.newAlias))
        tableBody.append(HEADER_STEAM_ID.format(candidate.steamId))
        tableBody.append(HEADER_PROFILE_LINK.format(candidate.url))

        output.append('\n'.join(tableBody))

    return output


def buildTargetsListMessage(candidates):
    print("building list message")
    output = []

    for candidate in candidates:
        tableBody = []
        tableBody.append(HEADER_NAME.format(candidate.name))
        tableBody.append(HEADER_ALIAS.format(candidate.newAlias))
        tableBody.append(HEADER_STEAM_ID.format(candidate.steamId))
        tableBody.append(HEADER_PROFILE_LINK.format(candidate.url))

        output.append('\n'.join(tableBody))

    return output


async def addTarget(message: discord.MessageType):
    print('adding a new target')

    command = message.content.strip()[5:]

    res = command.rpartition(' ')

    name = res[0]
    identifier = res[2]

    # if identifier is empty then we were not given an optional name
    if not identifier:
        name = ''
        identifier = res[0]

    print('split command into values name[{}] and identifier [{}]'.format(
        identifier, res[2]))

    # exists check
    query = db_conn.getTargetById(identifier)

    if not query.exists():
        result = getSteamIDFromSteamApi(identifier)

        steamId = ''
        newAlias = ''
        vanityURL = ''

        # if result from getSteamIDFromSteamApi is successful, then we are dealing with a vanity URL
        if result:
            steamId = result
            vanityURL = identifier
            newAlias = getSteamNameFromVanityId(identifier)
        else:
            steamId = identifier
            newAlias = getSteamNameFromSteamId(identifier)

        if not name:
            name = newAlias

        # check its valid steam profile
        if not newAlias:
            await clown(message)
            return

        # add records
        db_conn.putTarget(steamId, name, vanityURL)
        db_conn.updateChangeRecord(steamId, newAlias)

    # react to message
    await thumbsUp(message)


async def removeTarget(message: discord.MessageType):
    print('removing a target')

    # message valid
    if message.content.count(" ") < 1:
        await clown(message)

    command = message.content.strip()[8:]

    db_conn.deleteTarget(command)

    # react to message
    await thumbsUp(message)


async def listTargets(message: discord.MessageType):
    # load Target and latest alias
    targetList = db_conn.getTargets

    candidates = []

    for currentTarget in targetList:
        print("steam_id: {} age: {}".format(
            currentTarget.steam_id, currentTarget.name))

        result = db_conn.getLatestChangeById(currentTarget.steam_id)

        if not result.exists():
            continue

        candidates.append(candidate(currentTarget.name,
                          result.get().alias, '', currentTarget.steam_id, buildProfileDisplayURL(currentTarget)))

    targetList = buildTargetsListMessage(candidates)

    embedVar = discord.Embed(title="List of tracked entries", color=0x2986cc)
    for element in targetList:
        embedVar.add_field(name="", value=element, inline=False)

    await message.channel.send(embed=embedVar)


async def thumbsUp(message: discord.MessageType):
    emoji = '\N{Thumbs Up Sign}'
    if ('Zucchini' in message.author.name):
        await message.add_reaction('\N{Pregnant Woman}')
    else:
        await message.add_reaction(emoji)


async def thumbsDown(message: discord.MessageType):
    emoji = '\N{Thumbs Down Sign}'
    if ('Zucchini' in message.author.name):
        await message.add_reaction('\N{Pregnant Woman}')
    else:
        await message.add_reaction(emoji)


async def clown(message: discord.MessageType):
    emoji = '\N{Clown Face}'
    if ('Zucchini' in message.author.name):
        await message.add_reaction('\N{Pregnant Woman}')
    else:
        await message.add_reaction(emoji)


@client.event
async def on_message(message: discord.MessageType):
    print('there was a message by [{}] which says [{}]'.format(
        message.author, message.content))

    # exclude warbot so they dont get mad
    if (message.channel.name == 'warbot'):
        return

    # exclude non bot channels so they dont get mad
    if ('bot' not in message.channel.name):
        return

    if message.author == client.user:
        return

    if message.content.startswith("!add "):
        await addTarget(message)
        return

    if message.content.startswith("!remove "):
        await removeTarget(message)
        return

    if message.content.startswith("!list"):
        await listTargets(message)
        return

    # catchall
    if message.content.startswith("!"):
        await clown(message)
        return


@tasks.loop(seconds=POLLING_INTERVAL_SECONDS, count=None)
async def pollChangesJob():
    # load Target and latest alias
    target = db_conn.Target

    candidates = []

    for currentTarget in target.select():
        print("steam_id: {} age: {}".format(
            currentTarget.steam_id, currentTarget.name))

        # wget url and pull name
        newAlias = ''

        if currentTarget.vanity_url:
            newAlias = getSteamNameFromVanityId(currentTarget.vanity_url)
        else:
            newAlias = getSteamNameFromSteamId(currentTarget.steam_id)

        if not newAlias:
            # TODO handle not finding steam name
            print('COULD NOT FIND STEAM NAME!')
            continue

        # load lastest change and compare
        latestChange = db_conn.getLatestChangeById(currentTarget.steam_id)

        # If no change history, skip comparison and add to update candidates
        if not latestChange:
            db_conn.updateChangeRecord(currentTarget.steam_id,newAlias)
            candidates.append(candidate(currentTarget.name,
                              newAlias, '', currentTarget.steam_id, buildProfileDisplayURL(currentTarget)))
            continue

        print("we found the following previous steam name: [{}]".format(
            latestChange.alias))

        if latestChange.alias == newAlias:
            print("we found no name change, skipping")
            continue
            
        db_conn.updateChangeRecord(currentTarget.steam_id, newAlias)
        candidates.append(candidate(currentTarget.name, newAlias,
                          latestChange.alias, currentTarget.steam_id, buildProfileDisplayURL(currentTarget)))

    # if candidates populated update channels
    if candidates:
        print("we have candidates so we will build the update message")

        msg = buildMessage(candidates)

        channels = getChannelList(client.guilds)

        embedVar = discord.Embed(
            title="Steam Name Changes Detected", color=0xff0000)
        for thing in msg:
            embedVar.add_field(name="", value=thing, inline=False)

        for channel in channels:
            await channel.send(embed=embedVar)
    else:
        print("no candidates so we have nothing to do!")

    now = datetime.now()
    nextRunDts = now + timedelta(0, POLLING_INTERVAL_SECONDS)
    print("Polling complete. Next run at {}".format(
        nextRunDts.strftime("%d/%m/%Y %H:%M:%S")))


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    # Start the polling job
    if POLLING_JOB_ENABLED:
        pollChangesJob.start()

client.run(DISCORD_BOT_TOKEN)
