from database import db_conn
import requests
from lxml import objectify, etree, html
import variables

# Variables
STEAM_API_KEY = variables.STEAM_API_KEY
STEAM_COMMUNITY_TITLE_ERROR = variables.STEAM_COMMUNITY_TITLE_ERROR
STEAM_COMMUNITY_PROFILE_URL = variables.STEAM_COMMUNITY_PROFILE_URL
STEAM_COMMUNITY_ID_URL = variables.STEAM_COMMUNITY_ID_URL
STEAM_API_RESOLVE_VANITY_URL = variables.STEAM_API_RESOLVE_VANITY_URL
STEAM_STATUS_IN_GAME_TEXT = variables.STEAM_STATUS_IN_GAME_TEXT


class steamProfile:
    def __init__(self, name, status):
        self.name = name
        self.status = status


def build_profile_display_url(target: db_conn.Target):
    if target.vanity_url:
        return STEAM_COMMUNITY_ID_URL.format(target.vanity_url)
    else:
        return STEAM_COMMUNITY_PROFILE_URL.format(target.steam_id)


def get_steam_profile_page_content_from_url(url):
    return html.fromstring(requests.get(url).text)


def get_steam_status_from_content(content):
    print("retrieving target steam status")
    status_element = content.xpath("//div[contains(concat(' ', @class, ' '), ' profile_in_game_header ')]")
    if not status_element:
        return 'Private'

    status = status_element[0].text_content()[10:].strip()

    if status == STEAM_STATUS_IN_GAME_TEXT:
        game_element = content.xpath("//div[contains(concat(' ', @class, ' '), ' profile_in_game_name ')]")
        if game_element:
            game = game_element[0].text_content().strip()
            return status + ' ' + game

    return status


def get_steam_name_from_content(content):
    print("retrieving target steam name")
    # find a toner
    element = content.xpath("//title")
    if not element:
        return False

    title = element[0].text_content()

    if len(title) > 19 and not title == STEAM_COMMUNITY_TITLE_ERROR:
        name = title[19:]
        print("we found the following steam name: [{}]".format(name))
        return name
    else:
        print("unable to find Steam name")
        return False


def get_Steam_Profile_From_Steam_Id(id):
    print('retrieving target steam profile using their Steam ID')
    content = get_steam_profile_page_content_from_url(
        STEAM_COMMUNITY_PROFILE_URL.format(id))
    name = get_steam_name_from_content(content)
    status = get_steam_status_from_content(content)
    return steamProfile(name, status)


def get_steam_profile_from_vanity_id(id):
    print('retrieving target steam profile using their vanity ID')
    content = get_steam_profile_page_content_from_url(
        STEAM_COMMUNITY_ID_URL.format(id))
    name = get_steam_name_from_content(content)
    status = get_steam_status_from_content(content)
    return steamProfile(name, status)


def get_steam_profile(target: db_conn.Target):
    if target.vanity_url:
        return get_steam_profile_from_vanity_id(target.vanity_url)
    else:
        return get_Steam_Profile_From_Steam_Id(target.steam_id)


def get_steam_id_from_steam_api(id):
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
