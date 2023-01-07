from .errors import OpportunityNotSupported


sample_market = {
            "matchId": 349206,
            "id": 2087728,
            "name": "1X2",
            "status": 3,
            "type": 0,
            "category": 1,
            "selections": [
                {
                    "id": 6159208,
                    "name": "Draw",
                    "status": 1,
                    "odds": 5.14,
                    "handicap": None,
                    "total": None,
                    "type": "draw"
                },
                {
                    "id": 6159207,
                    "name": "Atalanta",
                    "status": 1,
                    "odds": 1.33,
                    "handicap": None,
                    "total": None,
                    "type": "home"
                },
                {
                    "id": 6159209,
                    "name": "Cremonese",
                    "status": 1,
                    "odds": 9.65,
                    "handicap": None,
                    "total": None,
                    "type": "away"
                }
            ],
            "order": 99999,
            "hasCombo": True,
            "hasInPlay": False,
            "isVisible": True,
            "overrideMainOrder": False,
            "handicap": None,
            "baseLine": None,
            "isMainLine": True,
            "lineMarketColumnNames": None
        }

def home_draw_away(market: dict) -> dict:
    opp_types = ["home", "draw", "away"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["selections"]:
            if outcome["type"] == opp_type:
                outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
    return dict(opportunities=outcomes, handicap=0.0)

# odd has to be first
def odd_even(market: dict) -> dict:
    opp_types = ["Odd", "Even"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["selections"]:
            if outcome["name"] == opp_type:
                outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
    return dict(opportunities=outcomes, handicap=0.0)

# home has to be first
def draw_no_bet(market: dict) -> dict:
    opp_types = ["home", "away"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["selections"]:
            if outcome["type"] == opp_type:
                outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
    return dict(opportunities=outcomes, handicap=0.0)

# yes has to be first
def yes_no(market: dict) -> dict:
    opp_types = ["Yes", "No"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["selections"]:
            if outcome["name"] == opp_type:
                outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
    return dict(opportunities=outcomes, handicap=0.0)



handle_supported_opportunities = {
    "1X2": {
        "func": home_draw_away,
        "bet_type": "1X2", # should be universal for every bookmaker
        "bet_scope": "full-time" #shoud be universal for every bookmaker
    },
    "1. Half Winner": {
        "func": home_draw_away,
        "bet_type": "1X2",
        "bet_scope": "first-half"
    },
    "2. Half Winner": {
        "func": home_draw_away,
        "bet_type": "1X2",
        "bet_scope": "second-half"
    },
    "Odd/Even": {
        "func": odd_even,
        "bet_type": "ODD_EVEN",
        "bet_scope": "full-time"
    },
    "1. Half Score Odd/Even": {
        "func": odd_even,
        "bet_type": "ODD_EVEN",
        "bet_scope": "first-half"
    },
    "2. Half Score Odd/Even": {
        "func": odd_even,
        "bet_type": "ODD_EVEN",
        "bet_scope": "second-half"
    },
    "Odd/Even - Home Team": {
        "func": odd_even,
        "bet_type": "ODD_EVEN_HOME",
        "bet_scope": "full-time"
    },
    "Odd/Even - Away Team": {
        "func": odd_even,
        "bet_type": "ODD_EVEN_AWAY",
        "bet_scope": "full-time"
    },
    "Draw No Bet": {
        "func": draw_no_bet,
        "bet_type": "DRAW_NO_BET",
        "bet_scope": "full-time"
    },
    "Both Teams To Score": {
        "func": yes_no,
        "bet_type": "BOTH_TO_SCORE",
        "bet_scope": "full-time"
    },
    "Both Teams To Score 1st Half": {
        "func": yes_no,
        "bet_type": "BOTH_TO_SCORE",
        "bet_scope": "first-half"
    },
    "Both Teams To Score 2nd Half": {
        "func": yes_no,
        "bet_type": "BOTH_TO_SCORE",
        "bet_scope": "second-half"
    },
}

def handle_opportunities(market: dict):
    try:
        handled_opps = handle_supported_opportunities[market["name"]]["func"](market)
        return dict(opportunities= handled_opps["opportunities"],
                    bet_type=  handle_supported_opportunities[market["name"]]["bet_type"],
                    bet_scope=  handle_supported_opportunities[market["name"]]["bet_scope"],
                    handicap= handled_opps["handicap"]
                    )
    except KeyError:
        raise OpportunityNotSupported("betting opportunity: {0} is not supported".format(market["name"]))