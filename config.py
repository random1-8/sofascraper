import browser
import pandas as pd
from pymongo import MongoClient

client = MongoClient()
db = client.sofascore_db

last_get = False
events_to_db = []

leagues_dict = {
    8:      "LaLiga",
    16:     "World Cup",
    17:     "Premier League",
    18:     "Championship",
    23:     "Serie A",
    34:     "Ligue 1",
    35:     "Bundesliga",
    155:    "Liga Profesional de Fútbol",
    325:    "Brasileiro Série A",
    11653:  "Primera Division"
}

columns = {
    "rival":                  pd.Series(dtype="str"),
    "venue":                  pd.Series(dtype="str"),
    "stadium":                pd.Series(dtype="str"),
    "country":                pd.Series(dtype="str"),
    "result":                 pd.Series(dtype="str"),
    "tournament":             pd.Series(dtype="str"),
    "date":                   pd.Series(dtype="str"),
    "status":                 pd.Series(dtype="str"),
    "goals_total":            pd.Series(dtype="int"),
    "goals_team":             pd.Series(dtype="int"),
    "goals_rival":            pd.Series(dtype="int"),
    "team_possession":        pd.Series(dtype="str"),
    "rival_possession":       pd.Series(dtype="str"),
    #"team_total_shots":       pd.Series(dtype="int"),
    #"rival_total_shots":      pd.Series(dtype="int"),
    #"team_shots_on_target":   pd.Series(dtype="int"),
    #"rival_shots_on_target":  pd.Series(dtype="int"),
    #"team_shots_off_target":  pd.Series(dtype="int"),
    #"rival_shots_off_target": pd.Series(dtype="int"),
    #"team_blocked_shots":     pd.Series(dtype="int"),
    #"rival_blocked_shots":    pd.Series(dtype="int"),
    "team_corners":           pd.Series(dtype="int"),
    "rival_corners":          pd.Series(dtype="int"),
    #"team_offsides":          pd.Series(dtype="int"),
    #"rival_offsides":         pd.Series(dtype="int"),
    #"team_fouls":             pd.Series(dtype="int"),
    #"rival_fouls":            pd.Series(dtype="int"),
    "team_yellow_cards":      pd.Series(dtype="int"),
    "rival_yellow_cards":     pd.Series(dtype="int"),
    "team_red_cards":         pd.Series(dtype="int"),
    "rival_red_cards":        pd.Series(dtype="int")
}

integer_stats = [
    "Total shots",
    "Shots on target",
    "Shots off target",
    "Blocked shots",
    "Corner kicks",
    "Offsides",
    "Fouls",
    "Yellow cards",
    "Red cards",
    "Big chances",
    "Big chances missed",
    "Shots inside box",
    "Shots outside box",
    "Goalkeeper saves",
    "Hit woodwork",
    "Counter attacks",
    "Counter attack shots",
    "Counter attack goals",
    "Passes",
    "Possession lost",
    "Duels won",
    "Aerials won",
    "Tackles",
    "Interceptions",
    "Clearances"
]

stats_to_add = [
    "Goals full time",
    "Ball possession",
    #"Total shots",
    #"Shots on target",
    #"Shots off target",
    #"Blocked shots",
    "Corner kicks",
    #"Offsides",
    #"Fouls",
    "Yellow cards",
    "Red cards"
]
driver = None

sofascore_api = "https://api.sofascore.com/api/v1"


def start_browser():
    global driver
    driver = browser.create_browser()


def quit_browser():
    global driver
    driver.quit()
