import discord
import variables

# TEST_MODE will only send to stebs place's channel
TEST_MODE_ENABLED = variables.TEST_MODE_ENABLED
STEBS_PLACE_CHANNEL_NAME = variables.STEBS_PLACE_CHANNEL_NAME
POLLING_INTERVAL_SECONDS = variables.POLLING_INTERVAL_SECONDS

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