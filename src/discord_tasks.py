import discord
from database import db_conn
from src import steam_utils
import variables
from discord.ext import tasks
from datetime import datetime, timedelta
from src import discord_utils

POLLING_INTERVAL_SECONDS = variables.POLLING_INTERVAL_SECONDS

@tasks.loop(seconds=POLLING_INTERVAL_SECONDS, count=None)
async def poll_profile_changes_job(client):
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