import browser
import config
import database
import helpers
from datetime import date, datetime

# Need to check more on this
# What if a match is currently suspended (e.g. bad weather, security issues)?
#
# I'm going to leave comments on match statuses and descriptions for reference.
# But don't know if I need to write other case than a finished match (type: "finished").
#
# Reference: any match that hasn't started yet
# code: 0, description: "Not started", type: "notstarted"
#
# Reference: any match being played in the first half
# code: 6, description: "1st half", type: "inprogress"
#
# Reference: any match being played in the second half
# code: 7, description: "2nd half", type: "inprogress"
#
# Reference: any match at halftime
# code: 31, description: "Halftime", type: "inprogress"
#
# Reference: Universidad de Chile v Unión Española, Copa Chile, url: https://api.sofascore.com/api/v1/event/10769752
# code: 60, description: "Postponed", type: "postponed"
#
# Reference: Iraq v Costa Rica, Int. Friendly Games, url: https://api.sofascore.com/api/v1/event/10885159
# code: 70, description: "Canceled", type: "canceled"
# Maybe the status can change, but on 2022-11-17 at 13:43 GMT-3 was canceled.
# Source: https://www.espn.com/soccer/costa-rica-crc/story/4804590/costa-rica-cancels-iraq-friendly-over-passport-issue
#
# Reference: any match that has ended in regular time (90 minutes)
# code: 100, description: "Ended", type: "finished"
#
# Reference: Boca Juniors v Racing Club, Trofeo de Campeones de la Liga Profesional, url: https://api.sofascore.com/api/v1/event/10857434
# code: 110, description: "AET", type: "finished"
#
# Reference: Senegal v Egypt, Africa Cup of Nations, url: https://api.sofascore.com/api/v1/event/10083105
# code: 120, description: "AP", type: "finished"
#
def full_time(event):
    if event["status"]["type"] == "finished":
        return True
    else:
        return False

# Example for Real Madrid last 30 matches
# https://api.sofascore.com/api/v1/team/2829/events/last/0
# If you need the next 30, increase the last digit by 1.
# Although historic data is massive, you need to check for "hasNextPage" attribute before increasing the last digit,
# or it will return a 404. 
def check_history(team_id, team_name, page_number = 0):
    team_last_matches = f"{config.sofascore_api}/team/{team_id}/events/last/"
    print(f"Checking {team_name} last matches, page {page_number}...")
    last_events_url = team_last_matches + str(page_number)
    last_events = browser.extract_json(last_events_url)
    return last_events

def parse_event(event_id):
    main_url        = f"{config.sofascore_api}/event/{event_id}"
    stats_url       = f"{main_url}/statistics"
    lineups_url     = f"{main_url}/lineups"
    incidents_url   = f"{main_url}/incidents"
    managers_url    = f"{main_url}/managers"

    event_main      = browser.extract_json(main_url)
    event_stats     = browser.extract_json(stats_url)
    event_lineups   = browser.extract_json(lineups_url)
    event_incidents = browser.extract_json(incidents_url)
    event_managers  = browser.extract_json(managers_url)
    
    # little check, it can save a request by checking first for statistics before actually requesting "event_stats"
    # but I don't think it has any value whatsoever and it could even fail in some cases.
    #if "hasEventPlayerStatistics" in event_main["event"] and event_main["event"]["hasEventPlayerStatistics"] and "statistics" not in event_stats:
    #    print(f"Check this event: {main_url}")
    #    raise Exception
    #elif "hasEventPlayerStatistics" in event_main["event"] and not event_main["event"]["hasEventPlayerStatistics"] and "statistics" in event_stats:
    #    print(f"Check this event: {main_url}")
    #    raise Exception
    #elif "hasEventPlayerStatistics" not in event_main["event"] and "statistics" in event_stats:
    #    print(f"Check this event: {main_url}")
    #    raise Exception

    # will throw a KeyError if a match has no statistics/incidents/lineups/managers, which apparently can happen.
    if "statistics" in event_stats:
        event_main["event"]["statistics"] = event_stats["statistics"]
    else:
        event_main["event"]["statistics"] = False

    if "incidents" in event_incidents:
        event_main["event"]["incidents"]  = event_incidents["incidents"]
    else:
        event_main["event"]["incidents"]  = False

    if "confirmed" in event_lineups and event_lineups["confirmed"]:
        event_main["event"]["lineups"]    = event_lineups
    else:
        event_main["event"]["lineups"]    = False

    if "homeManager" in event_managers and "awayManager" in event_managers:
        event_main["event"]["managers"]    = event_managers
    else:
        event_main["event"]["managers"]    = False
    
    id_renaming(event_main)

    return event_main["event"]


# Because Sofascore's JSONs has an "id" key all over the place and I don't want it to interfere with the DB id that Mongo will assign.
# Attribute "id" will be renamed to "sofaId"
# id_renaming() should be called before adding any kind of document to DB.
def id_renaming(d):
    for k in list(d.keys()):
        if isinstance(d[k], dict):
            id_renaming(d[k])
        elif isinstance(d[k], list):
            for i in d[k]:
                if isinstance(i, dict):
                    id_renaming(i)
        else:
            if k == "id":
                d["sofaId"] = d.pop(k)

def add_event(event):
    event_id       = event["id"]
    home_team_name = event["homeTeam"]["name"]
    away_team_name = event["awayTeam"]["name"]
    match = f"{home_team_name} v {away_team_name}"
    print(f"Searching {match}...")
    if database.already_exists("events", event_id):
        print(f"{match} on DB. Continue.\n")
    elif full_time(event):
        new_event = parse_event(event_id)
        config.events_to_db.append(new_event)
        print(f"{match} isn't on DB but has already finished. Match will be added to DB.\n")
    else:
        match_description = event["status"]["description"]
        print(f"{match} not on DB. Match status is: {match_description}\n")

# For daily events:
# Takes a date object.
# Loop through events of given date checking if they're finished or not.
# Will add to DB finished events that are not on DB (well obviously).
def catch_up(date):
    matchday = date.isoformat()
    events_url = f"{config.sofascore_api}/sport/football/scheduled-events/{matchday}"
    day_events = browser.extract_json(events_url)

    for event in day_events["events"]:
        unique_tournament_id = event["tournament"]["uniqueTournament"]["id"]
        if unique_tournament_id in config.leagues_dict:
            add_event(event)
    if config.events_to_db:
        print(f"{len(config.events_to_db)} events will be added to database.\n")
        config.db.events.insert_many(config.events_to_db)
        config.events_to_db = []

# Historic data for the national teams (well yes, but actually no).
# World Cup is around the corner so and I want to check the "process" of national teams,
# this being all matches since the current manager took charge.
# But it should be no difference with a club so you can enter any team_id you want.
def process(team_id, since=False):
    team_url = f"{config.sofascore_api}/team/{team_id}"
    team_json = browser.extract_json(team_url)
    team_manager = team_json["team"]["manager"]["id"]
    return 0


def team_history(team_id, team_name, since = False):
    since_timestamp = helpers.check_date(since)

    if since_timestamp:
        # search with date (many pages if necessary)
        page = 0
        too_far_back = False
        while not too_far_back:
            matches = check_history(team_id, team_name, page)
            matches_list = matches["events"]
            for event in reversed(matches_list):
                # reversed because "matches" is a list with events sorted by time ascending (past to present).
                # I need them backwards because when I find an event before the "since" parameter, I know that 
                # all the following events will be even further back and that means I can stop searching.
                if event["startTimestamp"] > since_timestamp:
                    add_event(event)
                else:
                    too_far_back = True
                    break
            if matches["hasNextPage"]:
                page += 1
            else:
                break

    else:
        # search only one page (last 30 matches)
        matches = check_history(team_id, team_name)
        matches_list = matches["events"]
        for event in reversed(matches_list):
            if event["startTimestamp"] > since_timestamp:
                add_event(event)
            else:
                break
    if config.events_to_db:
        print(f"{len(config.events_to_db)} events will be added to database.\n")
        config.db.events.insert_many(config.events_to_db)
        config.events_to_db = []

# Historic data from all teams on a tournament.
# Since a "unique_tournament" has many "tournaments" for now it will take the latest/ongoing tournament.
# "since" parameter should be a date, we don't want to grab records from the end of time do we?
# But to be honest I dont really know what the default value should be, current season for leagues?, last 30 matches?...
def unique_tournament(unique_tournament_id, since = False):
    root_url    = f"{config.sofascore_api}/unique-tournament/{unique_tournament_id}"
    seasons_url = f"{root_url}/seasons"
    unique_tournament_seasons = browser.extract_json(seasons_url)
    last_season_id = unique_tournament_seasons["seasons"][0]["id"]
    standings_url = f"{root_url}/season/{last_season_id}/standings/total"
    tournament = browser.extract_json(standings_url)

    table = tournament["standings"]
    # "table" is a list.
    # All tournaments are modeled the same, this being: "table" is a list of the groups of the tournament.
    # But what happens in a domestic league for example, since there are no groups?
    # Well a league is a tournament with one group, and every team is in this group.

    for group in table:
        for team in group["rows"]:
            team_id   = team["team"]["id"]
            team_name = team["team"]["name"]
            team_history(team_id, team_name, since)