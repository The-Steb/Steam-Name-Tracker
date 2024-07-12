import os

# Functionality variables
POLLING_INTERVAL_SECONDS = 60
POLLING_JOB_ENABLED = True
POST_UPDATES_ENABLED = False
EMOJI_REPLY_ENABLED = False
MESSAGE_REPLY_ENABLED = False

# TEST_MODE will only send to stebs place's channel
TEST_MODE_ENABLED = False
STEBS_PLACE_CHANNEL_NAME = 'bot_steb'

# OS Variables
STEAM_API_KEY = os.environ["STEAM_API_KEY"]
DISCORD_BOT_TOKEN = os.environ["BOT_TOKEN"]

# Static Variables
STEAM_COMMUNITY_TITLE_ERROR = 'Steam Community :: Error'
STEAM_STATUS_IN_GAME_TEXT = 'In-Game'
STEAM_COMMUNITY_PROFILE_URL = 'https://steamcommunity.com/profiles/{}/'
STEAM_COMMUNITY_ID_URL = 'https://steamcommunity.com/id/{}/'
STEAM_API_RESOLVE_VANITY_URL = 'https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}'

HEADER_NAME = '**Name**         |  {}'
HEADER_ALIAS = '**Alias**        |  __**{}**__'
HEADER_NEW_ALIAS = '**New Alias**        |  __**{}**__'
HEADER_STEAM_ID = '**Steam ID**     |  {}'
HEADER_PROFILE_LINK = '**Profile Link** |  {}'
HEADER_STATUS = '**Status**       |  **{}**'
HEADER_NEW_STATUS = '**New Status**   |  __**{}**__'

COMMANDS_HELP_TEXT = 'Tracker will poll for steam profile changes periodically and notify the discord channels.\nData is held in a Central Database, ALL tracked data is accessible within ALL of the discords that the bot is added to.\n\nThese are the tracker commands that can be used in various situations(do not include the triangle brackets: < or >):\n\nAdd/Remove tracker profiles\n   !help	View the list of tracker commands\n\nAdd/Remove tracker profiles\n   !add <name: Optional> <Steam ID: Mandatory>	Add a steam profile to the tracker\n   !remove <Steam ID: Mandatory>	Remove a steam profile from the tracker\n\nView held tracker data\n   !list <search term: Optional>	List the currently held tracker profile data, optionally search for names containing your search term\n'
