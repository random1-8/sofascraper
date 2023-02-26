from datetime import date, datetime

def check_date(date_param):
    date_timestamp = False
    if date_param and type(date_param) is date:
        # convert date_param to datetime
        date_converted = datetime.combine(date_param, datetime.min.time())
        date_timestamp = date_converted.timestamp()
    elif date_param and type(date_param) is not datetime:
        print(f"{date_param} is not a datetime object")
        raise Exception
    elif date_param:
        date_timestamp = date_param.timestamp()

    return date_timestamp




#if   stat_name == "Expected goals":
#elif stat_name == "Ball possession":
#elif stat_name == "Total shots":
#elif stat_name == "Shots on target":
#elif stat_name == "Shots off target":
#elif stat_name == "Blocked shots":
#elif stat_name == "Corner kicks":
#elif stat_name == "Offsides":
#elif stat_name == "Fouls":
#elif stat_name == "Yellow cards":
#elif stat_name == "Red cards":
#elif stat_name == "Big chances":
#elif stat_name == "Big chances missed":
#elif stat_name == "Shots inside box":
#elif stat_name == "Shots outside box":
#elif stat_name == "Goalkeeper saves":
#elif stat_name == "Hit woodwork":
#elif stat_name == "Counter attacks":
#elif stat_name == "Counter attack shots":
#elif stat_name == "Counter attack goals":
#elif stat_name == "Passes":
#elif stat_name == "Accurate passes":
#elif stat_name == "Long balls":
#elif stat_name == "Crosses":
#elif stat_name == "Dribbles":
#elif stat_name == "Possession lost":
#elif stat_name == "Duels won":
#elif stat_name == "Aerials won":
#elif stat_name == "Tackles":
#elif stat_name == "Interceptions":
#elif stat_name == "Clearances":