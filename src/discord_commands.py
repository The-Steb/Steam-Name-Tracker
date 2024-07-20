import discord
from database import db_conn
from src import steam_utils
from src import discord_utils
import variables

COMMANDS_HELP_TEXT = variables.COMMANDS_HELP_TEXT

async def help(message: discord.MessageType):
    print('sending help text')

    await message.reply(COMMANDS_HELP_TEXT)

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
            await discord_utils.clown(message)
            return

        # add records
        db_conn.putTarget(steamId, name, vanityURL, status)
        db_conn.putChangeRecord(steamId, newAlias)

    # react to message
    await discord_utils.thumbs_up(message)
    
async def remove_target(message: discord.MessageType):
    print('removing a target')

    # message valid
    if message.content.count(" ") < 1:
        await discord_utils.clown(message)

    command = message.content.strip()[8:]

    db_conn.deleteTarget(command)

    # react to message
    await discord_utils.thumbs_up(message)


async def list_targets(message: discord.MessageType):
    print('Listing all targets')
    
    # load command
    search_term = message.content.strip()[6:]
    
    print('Finding targets based on the search term [{}]'.format(search_term))
    
    # load Target and latest alias
    targetList = db_conn.get_targets_by_name(search_term)

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

        candidates.append(discord_utils.candidate(name,
                          previous_alias, '', steam_id, profile_url, status))

    elements = discord_utils.build_targets_list_message(candidates)

    embedVar = discord.Embed(title="List of tracked entries", color=variables.COLOUR_BLUE)

    for element in elements:
        embedVar.add_field(name="", value=element, inline=False)

    await message.reply(embed=embedVar)