import discord
from database import db_conn
from src import steam_utils
import variables

# TEST_MODE will only send to stebs place's channel
TEST_MODE_ENABLED = variables.TEST_MODE_ENABLED
STEBS_PLACE_CHANNEL_NAME = variables.STEBS_PLACE_CHANNEL_NAME

HEADER_NAME = variables.HEADER_NAME
HEADER_ALIAS = variables.HEADER_ALIAS
HEADER_NEW_ALIAS = variables.HEADER_NEW_ALIAS
HEADER_STEAM_ID = variables.HEADER_STEAM_ID
HEADER_PROFILE_LINK = variables.HEADER_PROFILE_LINK
HEADER_STATUS = variables.HEADER_STATUS
HEADER_NEW_STATUS = variables.HEADER_NEW_STATUS

class candidate:
    def __init__(self, name, newAlias, oldAlias, steamId, url, status):
        self.name = name
        self.newAlias = newAlias
        self.oldAlias = oldAlias
        self.steamId = steamId
        self.url = url
        self.status = status

def get_channel_list(client):
    print("building channel list")

    channels = []

    if TEST_MODE_ENABLED:
        print("TEST_MODE_ENABLED is turned on! building channel list")
        for channel in client.get_all_channels():
            # skip warbot so they dont get mad
            if (channel.name == STEBS_PLACE_CHANNEL_NAME):
                channels.append(channel)
        return channels

    for channel in client.get_all_channels():
        # skip warbot so they dont get mad
        if (channel.name == 'warbot'):
            continue

        if 'bot' in channel.name:
            channels.append(channel)
    return channels


def build_name_update_message(candidates):
    print("building update message")
    output = []

    for candidate in candidates:
        tableBody = []
        tableBody.append(HEADER_NAME.format(candidate.name))
        tableBody.append(HEADER_NEW_ALIAS.format(candidate.newAlias))
        tableBody.append(HEADER_STEAM_ID.format(candidate.steamId))
        tableBody.append(HEADER_PROFILE_LINK.format(candidate.url))
        tableBody.append(HEADER_STATUS.format(candidate.status))

        output.append('\n'.join(tableBody))

    return output

def build_status_update_message(candidates):
    print("building update message")
    output = []

    for candidate in candidates:
        tableBody = []
        tableBody.append(HEADER_NAME.format(candidate.name))
        tableBody.append(HEADER_ALIAS.format(candidate.newAlias))
        tableBody.append(HEADER_STEAM_ID.format(candidate.steamId))
        tableBody.append(HEADER_PROFILE_LINK.format(candidate.url))
        tableBody.append(HEADER_NEW_STATUS.format(candidate.status))

        output.append('\n'.join(tableBody))

    return output

def build_targets_list_message(candidates):
    print("building list message")
    output = []

    for candidate in candidates:
        tableBody = []
        tableBody.append(HEADER_NAME.format(candidate.name))
        tableBody.append(HEADER_ALIAS.format(candidate.newAlias))
        tableBody.append(HEADER_STEAM_ID.format(candidate.steamId))
        tableBody.append(HEADER_PROFILE_LINK.format(candidate.url))
        tableBody.append(HEADER_STATUS.format(candidate.status))

        output.append('\n'.join(tableBody))

    return output

async def add_target(message: discord.MessageType):
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

    if not query:
        result = steam_utils.get_steam_id_from_steam_api(identifier)

        steamId = ''
        newAlias = ''
        vanityURL = ''
        status = ''

        # if result from getSteamIDFromSteamApi is successful, then we are dealing with a vanity URL
        if result:
            steamId = result
            vanityURL = identifier
            profile: steam_utils.steamProfile = steam_utils.get_steam_profile_from_vanity_id(identifier)
            newAlias = profile.name
            status = profile.status
        else:
            steamId = identifier
            profile: steam_utils.steamProfile = steam_utils.get_Steam_Profile_From_Steam_Id(identifier)
            newAlias = profile.name
            status = profile.status

        if not name:
            name = newAlias

        # check its valid steam profile
        if not newAlias:
            await clown(message)
            return

        # add records
        db_conn.putTarget(steamId, name, vanityURL, status)
        db_conn.putChangeRecord(steamId, newAlias)

    # react to message
    await thumbs_up(message)


async def remove_target(message: discord.MessageType):
    print('removing a target')

    # message valid
    if message.content.count(" ") < 1:
        await clown(message)

    command = message.content.strip()[8:]

    db_conn.deleteTarget(command)

    # react to message
    await thumbs_up(message)


async def list_targets(message: discord.MessageType):
    print('Listing all targets')
    
    # load Target and latest alias
    target = db_conn.Target
    targetList = target.select()

    candidates = []

    for currentTarget in targetList:
        name = currentTarget.name
        steam_id = currentTarget.steam_id
        status = currentTarget.status
        profile_url = steam_utils.build_profile_display_url(currentTarget)

        result = db_conn.getLatestChangeById(steam_id)
        
        if not result:
            print('skipping target as no alias is on record')
            continue
        
        previous_alias = result.alias

        candidates.append(candidate(name,
                          previous_alias, '', steam_id, profile_url, status))

    elements = build_targets_list_message(candidates)

    embedVar = discord.Embed(title="List of tracked entries", color=0x2986cc)

    for element in elements:
        embedVar.add_field(name="", value=element, inline=False)

    await message.channel.send(embed=embedVar)


async def thumbs_up(message: discord.MessageType):
    emoji = '\N{Thumbs Up Sign}'
    if ('Zucchini' in message.author.name):
        await message.add_reaction('\N{Pregnant Woman}')
    else:
        await message.add_reaction(emoji)


async def thumbs_down(message: discord.MessageType):
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