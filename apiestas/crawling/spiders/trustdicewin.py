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
from ..utils.trustdicewin import handle_opportunities



class TrustDiceWinSpider(scrapy.Spider):
    name = Spiders.TRUSTDICE_WIN.value
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    download_delay = 0.25 # for testing purposes

    def __init__(self, sports: List[Sport] = None, bet_types: List[BetTypes] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.main_url = "https://api.trustdice.win/sports/"
        self.sports = None
        self.sport_params = [dict(sport="soccer")]
        self.bet_types = None
    
    def start_requests(self):
        logging.info("Getting tournaments for all of the sports")
        for sport_param in self.sport_params:
            params = {
                "format": "json",
                "lang": "en",
                "sport": sport_param["sport"],
                "tag": "upcoming"
            }
            encoded_params = urllib.parse.urlencode(params)
            yield scrapy.Request(url=f"{self.main_url}sport/?{encoded_params}", callback=self.parse_tournaments,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(sport_param=sport_param), dont_filter=True)

    def parse_tournaments(self, response, sport_param):
        logging.info("Parsing tournaments")
        try:
            decoded_response = response.body.decode("utf-8")
            parsed_response = json.loads(decoded_response)
            tournaments = parsed_response["results"]
            for tournament in tournaments:
                params = {
                    "format": "json",
                    "lang": "en",
                    "sport": sport_param["sport"],
                    "tag": "upcoming",
                    "category": tournament["category_url"],
                    "tournament": tournament["tournament_url"],
                    "count": tournament["tournament_count"]
                }
                encoded_params = urllib.parse.urlencode(params)
                yield scrapy.Request(url=f"{self.main_url}tournament/?{encoded_params}", callback=self.parse_matches,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(sport_param=sport_param), dont_filter=True)
        except Exception as e:
            logging.error(f"Getting Error while parsing tournaments with crawler: {self.name}, err: {e}")

    def parse_matches(self, response, sport_param):
        logging.info("Parsing matches")
        decoded_response = response.body.decode("utf-8")
        parsed_response = json.loads(decoded_response)
        tournament_keys = list(parsed_response["results"].keys())
        for tournament_key in tournament_keys:
            matches = parsed_response["results"][tournament_key]
            for match in matches:
                params = {
                    "format": "json",
                    "lang": "en",
                    "id": match["sport_event_obj_id"]
                }
                encoded_params = urllib.parse.urlencode(params)
                yield scrapy.Request(url=f"{self.main_url}event/?{encoded_params}", callback=self.parse_odds,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(sport_param=sport_param), dont_filter=True)

    def parse_odds(self, response, sport_param):
        logging.info("Parsing odds")
        try:
            decoded_response = response.body.decode("utf-8")
            parsed_response = json.loads(decoded_response)
            tournament = f"{parsed_response['category']} {parsed_response['tournament']}"
            match_obj = {
                "bookmaker": slugify(self.name),
                "sport": sport_param['sport'],
                # will be replaced by matcher slug/id
                "tournament": slugify(tournament),
                # tournament that is extracted from bookmaker
                "tournament_nice": tournament,
                "country": parsed_response["category"],
                "commence_time": int(datetime.strptime(parsed_response["scheduled_time"], "%Y-%m-%d %H:%M:%S").timestamp()),
                'teams': [parsed_response["home"], parsed_response["away"]],
                "url": ""
            }
            markets = parsed_response["markets"]
            bets = []
            for market in markets:
                try:
                    handled_opportunity = handle_opportunities(market, match_obj["teams"])
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
                    continue

            match = match_obj
            match['bets'] = bets
            yield Match(**match)
        except Exception as e:
            logging.error(f"Getting Error while parsing odds with crawler: {self.name}, err: {e}")

    def err_back(self, failure):
            # log all failures
            logging.error(f"Getting Error while sending request with crawler: {self.name}, err: {repr(failure)}")