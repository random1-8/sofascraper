import config
import copy
import helpers
import pandas as pd
from datetime import datetime

def row_from_event(event, team_id):
    team       = event["homeTeam"]["name"]
    rival      = event["awayTeam"]["name"]
    try:
        stadium = event["venue"]["stadium"]["name"]
        city    = event["venue"]["city"]["name"]
        country = event["venue"]["country"]["name"]
        stadium_full = f"{stadium}, {city}"
    except KeyError:
        stadium_full = ""
        country      = ""
    tournament = event["tournament"]["uniqueTournament"]["name"]
    date       = datetime.fromtimestamp(event["startTimestamp"]).strftime("%Y-%m-%d")
    status     = event["status"]["description"]
    winner     = event["winnerCode"]

    home_stats = {
        "Goals full time":  "",
        "Ball possession":  "",
        "Total shots":      0,
        "Shots on target":  0,
        "Shots off target": 0,
        "Blocked shots":    0,
        "Corner kicks":     0,
        "Offsides":         0,
        "Fouls":            0,
        "Yellow cards":     0,
        "Red cards":        0
    }
    away_stats = copy.copy(home_stats)
    home_stats["Goals full time"] = event["homeScore"]["normaltime"]
    away_stats["Goals full time"] = event["awayScore"]["normaltime"]

    stats = event["statistics"]
    # stats: list of dictioraries
    # every dict is a period in the match, e.g. 1ST, 2ND, ALL
    # for now, ALL
    for period in stats:
        if period["period"] == "ALL":
            groups = period["groups"]
            # groups: list of dictioraries
            # groups as in "group similar stats"
            # e.g. "shots" group has: "on target", "off target"...
            for group in groups:
                #stat_group_name = group["groupName"]
                stat_detail     = group["statisticsItems"]
                # stat_detail: list of dictioraries
                # detailed stat for a group
                # has name of stat, values for home/away
                for stat in stat_detail:
                    stat_name  = stat["name"]
                    home_value = stat["home"]
                    away_value = stat["away"]
                    if   stat_name == "Expected goals":
                        home_value = float(home_value)
                        away_value = float(away_value)
                    elif stat_name in config.integer_stats:
                        home_value = int(home_value)
                        away_value = int(away_value)
                    home_stats[stat_name] = home_value
                    away_stats[stat_name] = away_value

    result = "D"
    if event["homeTeam"]["sofaId"] == team_id:
        venue_code = "Home"
        if   winner == 1:
            result = "W"
        elif winner == 2:
            result = "L"
    else:
        home_stats, away_stats = away_stats, home_stats
        team, rival = rival, team
        venue_code = "Away"
        if   winner == 1:
            result = "L"
        elif winner == 2:
            result = "W"
    goals_total_full_time = home_stats["Goals full time"] + away_stats["Goals full time"]
    row = [
        rival,
        venue_code,
        stadium_full,
        country,
        result,
        tournament,
        date,
        status,
        goals_total_full_time
    ]
    if len(home_stats) != len(away_stats):
        raise

    for key in home_stats:
        if key in config.stats_to_add:
            row.append(home_stats[key])
            row.append(away_stats[key])

    return team, row

def create_from_teams(teams_list, since = False, limit = 0):
    if type(teams_list) is not list:
        print(f"{teams_list} is not a list.")
        raise Exception
    if limit and type(limit) is not int:
        print(f"{limit} is not an int.")
        raise Exception
    if limit and type(limit) is int and limit < 0:
        print(f"{limit} is less than zero (0)")
        raise Exception

    events_col = config.db.events
    since_timestamp = helpers.check_date(since)
    now_formatted = datetime.now().strftime("%Y-%d-%m_%H.%M.%S")
    filename = f"teams_statistics_{now_formatted}.xlsx"

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    for team in teams_list:
        query = {
            "$or": [
                {"homeTeam.sofaId": team},
                {"awayTeam.sofaId": team}
            ],
            "statistics": {"$ne" : False}
        }
        if since_timestamp:
            query["startTimestamp"] = {"$gt": since_timestamp}
        results = events_col.find(query).sort("startTimestamp", -1).limit(limit)

        df = pd.DataFrame(columns=config.columns)
        for event in results:
            team_name, new_row = row_from_event(event, team)
            try: 
                # add row to dataframe
                df.loc[len(df)] = new_row
            except ValueError:
                breakpoint()


        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name=team_name, index=False)

    writer.close()

def create_from_tournament(unique_tournament_id, season_id, since = False, limit = False):
    tournaments_col = config.db.tournaments

    since_timestamp = helpers.check_date(since)


    return 0
