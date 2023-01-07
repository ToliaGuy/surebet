import logging
from typing import List
import urllib
import json
from datetime import datetime
from dateutil import parser


import scrapy
from slugify import slugify

from capiestas.crawling.items import Match, Bet
from capiestas.crawling.enums import Spiders, BetTypes
from capiestas.api.app.models.enums import Sport
from capiestas.metrics import set_testing_metric
from ..utils.errors import OpportunityNotSupported
from ..utils.thunderpick import handle_opportunities
from ..utils.utils import thunderpick_country

class ThunderPickSpider(scrapy.Spider):
    name = Spiders.THUNDER_PICK.value
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    download_delay = 0.25 # for testing purposes

    def __init__(self, sports: List[Sport] = None, bet_types: List[BetTypes] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.main_url = "https://thunderpick.com/"
        self.sports = None
        self.sport_params = [dict(sport="soccer", sport_url="football", game_id=10)]
        self.bet_types = None


    def start_requests(self):
        logging.info("Getting tournaments for all of the sports")
        for sport_param in self.sport_params:
            data = {
                "competitionId": None,
                "country": None,
                "gameIds": [sport_param["game_id"]]
            }
            encoded_data = json.dumps(data)
            yield scrapy.Request(url=f"{self.main_url}api/matches", method='POST', body=encoded_data,
            callback=self.parse_matches, errback=self.err_back, headers={'User-Agent': self.user_agent, 'Content-Type': 'application/json'},
            cb_kwargs=dict(sport_param=sport_param), dont_filter=True)

    def parse_matches(self, response, sport_param):
        logging.info("Parsing matches")
        try:
            decoded_response = response.body.decode("utf-8")
            parsed_response = json.loads(decoded_response)
            matches = parsed_response["data"]["upcoming"]
            for match in matches:
                match_id = match["id"]
                tournament = f"{thunderpick_country[match['competition']['countryCode']]} {match['competition']['name']}"
                match_obj = {
                    "bookmaker": slugify(self.name),
                    "sport": sport_param['sport'],
                    # will be replaced by matcher slug/id
                    "tournament": slugify(tournament),
                    # tournament that is extracted from bookmaker
                    "tournament_nice": tournament,
                    "country": "",
                    "commence_time": int(datetime.strptime(match["startTime"], "%Y-%m-%dT%H:%M:%S%z").timestamp()),
                    'teams': [match["teams"]["home"]["name"], match["teams"]["away"]["name"]],
                    # will add later
                    "url": ""
                }
                yield scrapy.Request(url=f"{self.main_url}api/markets/{match_id}", callback=self.parse_odds,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(match_obj = match_obj), dont_filter=True)
        except Exception as e:
            logging.error(f"Getting Error while parsing matches with crawler: {self.name}, err: {e}")


    def parse_odds(self, response, match_obj):
        set_testing_metric()
        logging.info("Parsing odds")
        try:
            decoded_response = response.body.decode("utf-8")
            parsed_response = json.loads(decoded_response)
            markets = parsed_response["data"]
            match = match_obj
            bets = []
            for market in markets:
                try:
                    handled_opportunity = handle_opportunities(market)
                    bet_dict = {
                        "bookmaker": slugify(self.name),
                        "bookmaker_nice": self.name,
                        "is_back": True,
                        "bet_type": handled_opportunity["bet_type"],
                        "bet_scope": handled_opportunity["bet_scope"],
                        "bet_category": market["name"],
                        "handicap": handled_opportunity["handicap"],
                        "url": "",
                        "feed": "",
                        "opportunities": handled_opportunity["opportunities"]
                    }
                    logging.info(bet_dict)
                    # choose what information gets passed into the bet object
                    bet = Bet(**bet_dict)
                    bets.append(bet)
                except OpportunityNotSupported:
                    # I can also implement some functionality, for example that if the the opportunity is not
                    # supported than I can collect them in DB and than explore them in browser without the need
                    # of finding it on the bookmaker site
                    continue

            match['bets'] = bets
            yield Match(**match)
        except Exception as e:
            logging.error(f"Getting Error while parsing odds with crawler: {self.name}, err: {e}")


    def err_back(self, failure):
            # log all failures
            logging.error(f"Getting Error while sending request with crawler: {self.name}, err: {repr(failure)}")