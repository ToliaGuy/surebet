import re
from .errors import OpportunityNotSupported


sample_market = {
   "id":"1",
   "marketId":"1",
   "specifiers":{
      
   },
   "name":"1x2",
   "localizations":{
      "en":"1x2",
      "de":"1x2",
      "it":"1x2",
      "pt":"1x2",
      "es":"1x2"
   },
   "groups":[
      "all",
      "score",
      "regular_play"
   ],
   "markets":[
      {
         "id":"d520e5f4-21e7-4b79-ac94-5b5803f194b6",
         "status":"active",
         "outcomes":[
            {
               "id":"b7555a72-f54c-4d46-adc0-b27ba70ee25a",
               "extId":"3",
               "active":True,
               "result":"None",
               "odds":2.35,
               "name":"Pacific",
               "localizations":{
                  "en":"Pacific",
                  "de":"Pacific",
                  "it":"Pacific",
                  "pt":"Pacific",
                  "es":"Pacific"
               }
            },
            {
               "id":"c092196b-d2fd-4dfa-a88a-6ef13f05a4c9",
               "extId":"1",
               "active":True,
               "result":"None",
               "odds":2.8,
               "name":"HFX",
               "localizations":{
                  "en":"HFX",
                  "de":"HFX",
                  "it":"HFX",
                  "pt":"HFX",
                  "es":"HFX"
               }
            },
            {
               "id":"c83ab42a-9f45-43bc-9b46-9cab077859fb",
               "extId":"2",
               "active":True,
               "result":"None",
               "odds":3.3,
               "name":"draw",
               "localizations":{
                  "en":"draw",
                  "de":"unentschieden",
                  "it":"pareggio",
                  "pt":"empate",
                  "es":"empate"
               }
            }
         ]
      }
   ]
}



def home_draw_away(market: dict) -> list:
    opp_types = ["1", "2", "3"]
    outcomes = list()
    for opp_type in opp_types:
        for outcome in market["markets"][0]["outcomes"]:
            if outcome["extId"] == opp_type:
                outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
    return [dict(opportunities=outcomes, handicap=0.0)]

# when calculating under/over under should be always first over always second
def over_under(market: dict) -> list:
   opp_types = ["under", "over"]
   final = list()
   for markt in market["markets"]:
      outcomes = list()
      handicap = 0
      for opp_type in opp_types:
         for outcome in markt["outcomes"]:
            if opp_type in outcome["name"]:
               handicap = float(outcome["name"].replace("under ", "").replace("over", ""))
               outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
      final.append(dict(opportunities=outcomes, handicap=handicap))
   return final

def handicap(market: dict)-> list:
   final = list()
   for markt in market["markets"]:
      outcomes = list()
      handicap = 0.0
      first_ext_id = 0
      try:
         for outcome in markt["outcomes"]:
            if len(outcomes) == 0:
               first_ext_id = int(outcome["extId"])
               outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
            # means that this is not first outcome so we should find out what the order
            # of the opportunities
            # smaller ext id is always home so if current extid is smaller than first one
            # that means that this is home and we need to prepend it to the array
            elif first_ext_id > int(outcome["extId"]):
               outcomes.insert(0, dict(label=outcome["name"], odd=outcome["odds"]))
            elif first_ext_id < int(outcome["extId"]):
               outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))

         handicap_value_str = re.findall(r'\((.*?)\)', outcomes[0]["label"])[-1]
         handicap = float(handicap_value_str)
         final.append(dict(opportunities=outcomes, handicap=handicap))

      # some handicaps are for example: Arsenal (1:0) which will throw valueError when
      # float("1:0")
      except ValueError as e:
         print(e)
         continue
   return final

# odd has to be first
def odd_even(market: dict) -> list:
   opp_types = ["odd", "even"]
   outcomes = list()
   for opp_type in opp_types:
     for outcome in market["markets"][0]["outcomes"]:
         if outcome["name"] == opp_type:
             outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
   return [dict(opportunities=outcomes, handicap=0.0)]

def draw_no_bet(market: dict) -> list:
   opp_types = ["4", "5"]
   outcomes = list()
   for opp_type in opp_types:
      for outcome in market["markets"][0]["outcomes"]:
         if outcome["extId"] == opp_type:
               outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
   return [dict(opportunities=outcomes, handicap=0.0)]

def yes_no(market: dict) -> list:
   opp_types = ["yes", "no"]
   outcomes = list()
   for opp_type in opp_types:
      for outcome in market["markets"][0]["outcomes"]:
         if outcome["name"] == opp_type:
               outcomes.append(dict(label=outcome["name"], odd=outcome["odds"]))
   return [dict(opportunities=outcomes, handicap=0.0)]

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
        handled_opps = handle_supported_opportunities[processed_name]["func"](market)
        return dict(opportunities= handled_opps,
                    bet_type=  handle_supported_opportunities[processed_name]["bet_type"],
                    bet_scope=  handle_supported_opportunities[processed_name]["bet_scope"],
                    )
    except KeyError:
        raise OpportunityNotSupported("betting opportunity: {0} is not supported".format(market["name"]))