import re
from .errors import OpportunityNotSupported


sample_market = {
            "id": 308,
            "market_external_id": 1,
            "match_urn_id": "sr:match:35644171",
            "name": "1x2",
            "specifier": "",
            "status": 1,
            "outcomes": [
                {
                    "id": 844,
                    "outcome_external_id": "1",
                    "active": True,
                    "name": "Borussia Dortmund",
                    "odds": 1350
                },
                {
                    "id": 845,
                    "outcome_external_id": "2",
                    "active": True,
                    "name": "draw",
                    "odds": 5820
                },
                {
                    "id": 846,
                    "outcome_external_id": "3",
                    "active": True,
                    "name": "FC Copenhagen",
                    "odds": 8020
                }
            ],
            "priority": 1,
            "most_balanced": False,
            "market_groups": [
                "all",
                "top"
            ],
            "custom_bet_groups": [],
            "provider": "betradar"
        }

def home_draw_away(market: dict) -> dict:
    opp_types = ["1", "2", "3"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["outcomes"]:
            if opp_type == outcome["outcome_external_id"]:
                odd = outcome["odds"] / 1000
                outcomes.append(dict(label=outcome["name"], odd=odd))
    return dict(opportunities=outcomes, handicap=0.0)

# when calculating under/over under should be always first over always second
def over_under(market: dict) -> dict:
    opp_types = ["under", "over"]
    outcomes = list()
    handicap = 0
    for opp_type in opp_types:
        for outcome in market["outcomes"]:
            if opp_type in outcome["name"]:
                handicap = float(outcome["name"].replace("under ", "").replace("over ", ""))
                odd = outcome["odds"] / 1000
                outcomes.append(dict(label=outcome["name"], odd=odd))
    return dict(opportunities=outcomes, handicap=handicap)

# when calculating handicap when home has positive handicap than handicap parameter is
# positive and that means that first handicap is positive home second is negative away
def handicap(market: dict) -> dict:
    """
    We are going through the outcomes and comparing their handicap value with specifier
    specifier has always value of home, so basically if handicap value is same as specifier
    and outcomes are empty than we are inserting home and if the handicap value is complete opposite of
    specifier than we know that this is away opportunity and we are inserting value into outcomes only when
    there already is something - gets tricky with handicap 0 so I need to explicitly check if it is -0 or +0
    """
    outcomes = list()
    handicap = float(market["specifier"].replace("hcp=", ""))
    # we have double loop because we dont know the order in which opportunities are home can be first or away can be first
    for x in market["outcomes"]:
        for outcome in market["outcomes"]:
            handicap_value_str = re.findall(r'\((.*?)\)', outcome["name"])[-1]
            handicap_value = float(handicap_value_str)
            if (handicap_value_str == "+0" or handicap_value_str != "-0") and handicap == handicap_value:
                if len(outcomes) == 0:
                    odd = outcome["odds"] / 1000
                    outcomes.append(dict(label=outcome["name"], odd=odd))
            elif (handicap_value_str == "-0" or handicap_value_str != "+0") and handicap == (handicap_value*-1):
                if len(outcomes) == 1:
                    odd = outcome["odds"] / 1000
                    outcomes.append(dict(label=outcome["name"], odd=odd))
    return dict(opportunities=outcomes, handicap=handicap)

def odd_even(market: dict) -> dict:
    opp_types = ["odd", "even"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["outcomes"]:
            if outcome["name"] == opp_type:
                odd = outcome["odds"] / 1000
                outcomes.append(dict(label=outcome["name"], odd=odd))
    return dict(opportunities=outcomes, handicap=0.0)


def draw_no_bet(market: dict) -> dict:
    opp_types = ["4", "5"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["outcomes"]:
            if opp_type == outcome["outcome_external_id"]:
                odd = outcome["odds"] / 1000
                outcomes.append(dict(label=outcome["name"], odd=odd))
    return dict(opportunities=outcomes, handicap=0.0)


def yes_no(market: dict) -> dict:
   opp_types = ["yes", "no"]
   outcomes = list()
   for opp_type in opp_types:
      for outcome in market["outcomes"]:
         if outcome["name"] == opp_type:
            odd = outcome["odds"] / 1000
            outcomes.append(dict(label=outcome["name"], odd=odd))
   return dict(opportunities=outcomes, handicap=0.0)


handle_supported_opportunities = {
    "1x2": {
            "func": home_draw_away,
            "bet_type": "1X2", # should be universal for every bookmaker
            "bet_scope": "full-time" #shoud be universal for every bookmaker
    },
    "1st half - 1x2": {
        "func": home_draw_away,
        "bet_type": "1X2",
        "bet_scope": "first-half"
    },
    "2nd half - 1x2": {
        "func": home_draw_away,
        "bet_type": "1X2",
        "bet_scope": "second-half"
    },
    "Total": {
      "func": over_under,
      "bet_type": "TOTAL",
      "bet_scope": "full-time"
    },
    "1st half - total": {
      "func": over_under,
      "bet_type": "TOTAL",
      "bet_scope": "first-half"
    },
    "2nd half - total": {
      "func": over_under,
      "bet_type": "TOTAL",
      "bet_scope": "second-half"
    },
    "HOME total": {
      "func": over_under,
      "bet_type": "HOME_TOTAL",
      "bet_scope": "full-time"
    },
    "AWAY total": {
      "func": over_under,
      "bet_type": "AWAY_TOTAL",
      "bet_scope": "full-time"
    },
    "1st half - HOME total": {
      "func": over_under,
      "bet_type": "HOME_TOTAL",
      "bet_scope": "first-half"
    },
    "1st half - AWAY total": {
      "func": over_under,
      "bet_type": "AWAY_TOTAL",
      "bet_scope": "first-half"
    },
    "2nd half - HOME total": {
      "func": over_under,
      "bet_type": "HOME_TOTAL",
      "bet_scope": "second-half"
    },
    "2nd half - AWAY total": {
      "func": over_under,
      "bet_type": "AWAY_TOTAL",
      "bet_scope": "second-half"
    },
    "Handicap": {
      "func": handicap,
      "bet_type": "HANDICAP",
      "bet_scope": "full-time"
    },
    "1st half - handicap": {
      "func": handicap,
      "bet_type": "HANDICAP",
      "bet_scope": "first-half"
    },
    "2nd half - handicap": {
      "func": handicap,
      "bet_type": "HANDICAP",
      "bet_scope": "second-half"
    },
    "Odd/even": {
        "func": odd_even,
        "bet_type": "ODD_EVEN",
        "bet_scope": "full-time"
    },
    "1st half - odd/even": {
        "func": odd_even,
        "bet_type": "ODD_EVEN",
        "bet_scope": "first-half"
    },
    "2nd half - odd/even": {
        "func": odd_even,
        "bet_type": "ODD_EVEN",
        "bet_scope": "second-half"
    },
    "HOME odd/even": {
        "func": odd_even,
        "bet_type": "ODD_EVEN_HOME",
        "bet_scope": "full-time"
    },
    "AWAY odd/even": {
        "func": odd_even,
        "bet_type": "ODD_EVEN_AWAY",
        "bet_scope": "full-time"
    },
    "Draw no bet": {
        "func": draw_no_bet,
        "bet_type": "DRAW_NO_BET",
        "bet_scope": "full-time"
    },
    "1st half - draw no bet":{
        "func": draw_no_bet,
        "bet_type": "DRAW_NO_BET",
        "bet_scope": "first-half"
    },
    "2nd half - draw no bet":{
        "func": draw_no_bet,
        "bet_type": "DRAW_NO_BET",
        "bet_scope": "second-half"
    },
    "Both teams to score": {
        "func": yes_no,
        "bet_type": "BOTH_TO_SCORE",
        "bet_scope": "full-time"
    },
    "1st half - both teams to score": {
        "func": yes_no,
        "bet_type": "BOTH_TO_SCORE",
        "bet_scope": "first-half"
    },
    "2nd half - both teams to score": {
        "func": yes_no,
        "bet_type": "BOTH_TO_SCORE",
        "bet_scope": "second-half"
    },
}


def handle_opportunities(market: dict, teams: list) -> dict:
    try:
        processed_name = market["name"].replace(teams[0], "HOME").replace(teams[1], "AWAY")
        print(processed_name)
        handled_opps = handle_supported_opportunities[processed_name]["func"](market)
        return dict(opportunities= handled_opps["opportunities"],
                    bet_type=  handle_supported_opportunities[processed_name]["bet_type"],
                    bet_scope=  handle_supported_opportunities[processed_name]["bet_scope"],
                    handicap= handled_opps["handicap"]
                    )
    except KeyError:
        raise OpportunityNotSupported("betting opportunity: {0} is not supported".format(market["name"]))