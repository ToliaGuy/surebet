import re
from .errors import OpportunityNotSupported


sample_market = {
                'market_id': '1',
                'name': '1x2',
                'specifiers': None,
                'status': 1,
                'outcomes': 
                    [
                        {
                            'outcome_id': '1',
                            'name': 'Skive IK',
                            'odds': '1.74',
                            'probabilities': '0.532585',
                            'active': True,
                            'id': '38249673|1'
                        },
                        {
                            'outcome_id': '2',
                            'name': 'draw',
                            'odds': '3.8',
                            'probabilities': '0.230727',
                            'active': True,
                            'id': '38249673|2'
                        }, 
                        {
                            'outcome_id': '3',
                            'name': 'BK Frem',
                            'odds': '3.7',
                            'probabilities': '0.236688',
                            'active': True,
                            'id': '38249673|3'
                        }
                    ],
                'id': 38249673
            }


def home_draw_away(market: dict) -> dict:
    opp_types = ["1", "2", "3"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["outcomes"]:
            if opp_type == outcome["outcome_id"]:
                outcomes.append(dict(label=outcome["name"], odd=float(outcome["odds"])))
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
                outcomes.append(dict(label=outcome["name"], odd=float(outcome["odds"])))
    return dict(opportunities=outcomes, handicap=handicap)



# when calculating handicap when home has positive handicap than handicap parameter is
# positive and that means that first handicap is positive home second is negative away
def handicap(market: dict) -> dict:
    """
    We are going through the outcomes and comparing their handicap value with specifier
    specifier has always value of home, so basically if handicap value is same as specifier
    and outcomes are empty than we are inserting home and if the handicap value is complete opposite of
    specifier than we know that this is away opportunity and we are inserting value into outcomes only when
    there already is something - gets tricky with handicap 0 but in this case it is alway +0 so we just need to
    believe that first is home and second is away
    """
    outcomes = list()
    handicap = float(market["specifiers"].replace("hcp=", ""))
    # we have double loop because we dont know the order in which opportunities are home can be first or away can be first
    for x in market["outcomes"]:
        for outcome in market["outcomes"]:
            handicap_value_str = re.findall(r'\((.*?)\)', outcome["name"])[-1]
            handicap_value = float(handicap_value_str)
            # in case of 0 it will be alway equal, therefore I added elif
            if handicap == handicap_value:
                if len(outcomes) == 0:
                    outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
                elif handicap_value_str == "+0" and len(outcomes) == 1:
                    outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))

            elif handicap == (handicap_value*-1):
                if len(outcomes) == 1:
                    outcomes.append(dict(label=outcome["name"], odd=outcome["odds"] ))
    return dict(opportunities=outcomes, handicap=handicap)

def odd_even(market: dict) -> dict:
    opp_types = ["odd", "even"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["outcomes"]:
            if outcome["name"] == opp_type:
                outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
    return dict(opportunities=outcomes, handicap=0.0)


def draw_no_bet(market: dict) -> dict:
    opp_types = ["4", "5"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["outcomes"]:
            if opp_type == outcome["outcome_id"]:
                outcomes.append(dict(label=outcome["name"], odd=float(outcome["odds"])))
    return dict(opportunities=outcomes, handicap=0.0)


def yes_no(market: dict) -> dict:
   opp_types = ["yes", "no"]
   outcomes = list()
   for opp_type in opp_types:
      for outcome in market["outcomes"]:
         if outcome["name"] == opp_type:
               outcomes.append(dict(label=outcome["name"], odd=float(outcome["odds"])))
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
    except KeyError as e:
        print(e)
        raise OpportunityNotSupported("betting opportunity: {0} is not supported".format(market["name"]))
    except Exception as e:
        print(e)