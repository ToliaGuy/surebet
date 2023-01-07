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
from ..utils.errors import OpportunityNotSupported
from ..utils.n1bet import handle_opportunities



class N_OneBetSpider(scrapy.Spider):
    name = Spiders.N_ONE_BET.value
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    download_delay = 0.25 # for testing purposes


    def __init__(self, sports: List[Sport] = None, bet_types: List[BetTypes] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.main_url = "https://n1bet.com/"
        self.sports = None
        self.sport_params = [dict(sport="soccer", sport_url="soccer")]
        self.bet_types = None

    def start_requests(self):
        logging.info("Getting tournaments for all of the sports")
        for sport_param in self.sport_params:
            params = {
                "bettable": True,
                "limit": 500,
                "match_status": 0,
                "sport_key": sport_param["sport_url"]
            }
            encoded_params = urllib.parse.urlencode(params)
            yield scrapy.Request(url=f"{self.main_url}api/v2/tournaments?{encoded_params}", callback=self.parse_tournaments,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(sport_param=sport_param), dont_filter=True)

    def parse_tournaments(self, response, sport_param):
        logging.info("Parsing tournaments")
        try:
            decoded_response = response.body.decode("utf-8")
            parsed_response = json.loads(decoded_response)
            tournaments = parsed_response["data"]
            for tournament in tournaments:
                tournament_id = tournament["id"]
                tournament_name = f"{tournament['category']['name']} {tournament['name']}"
                tournament_country = tournament["category"]["name"]
                params = {
                    "bettable": True,
                    "limit": 500,
                    "match_status": 0,
                    "sort_by": "tournament.priority:asc",
                    "sort_by": "tournament.id:asc",
                    "sort_by": "start_time:asc",
                    "sort_by": "bets_count:desc",
                    "tournament_id": tournament_id,
                    "type": "match"
                }
                encoded_params = urllib.parse.urlencode(params)
                yield scrapy.Request(url=f"{self.main_url}api/v2/matches?{encoded_params}", callback=self.parse_matches,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(sport_param=sport_param, tournament_name=tournament_name, tournament_country=tournament_country), dont_filter=True)

        except Exception as e:
            logging.error(f"Getting Error while parsing tournaments with crawler: {self.name}, err: {e}")

    def parse_matches(self, response, sport_param, tournament_name, tournament_country):
        logging.info("Parsing matches")
        try:
            decoded_response = response.body.decode("utf-8")
            parsed_response = json.loads(decoded_response)
            matches = parsed_response["data"]
            for match in matches:
                match_id = match["id"]
                match_url = f"{self.main_url}en/{sport_param['sport_url']}/{match['slug']}-m-{match['id']}"
                match_obj = {
                    "bookmaker": slugify(self.name),
                    "sport": sport_param['sport'],
                    # will be replaced by matcher slug/id
                    "tournament": slugify(tournament_name),
                    # tournament that is extracted from bookmaker
                    "tournament_nice": tournament_name,
                    "country": tournament_country,
                    # can also do int(datetime.strptime(match["start_time"], "%Y-%m-%dT%H:%M:%SZ").timestamp())
                    # because this time is in UTC
                    "commence_time": int(datetime.strptime(match["start_time"], "%Y-%m-%dT%H:%M:%S%z").timestamp()),
                    'teams': [match["competitors"]["home"]["name"], match["competitors"]["away"]["name"]],
                    "url": match_url
                }
                params = {
                    "limit": 500
                }
                encoded_params = urllib.parse.urlencode(params)
                yield scrapy.Request(url=f"{self.main_url}api/v2/matches/{match_id}/markets?{encoded_params}", callback=self.parse_odds,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(match_obj = match_obj), dont_filter=True)

        except Exception as e:
            logging.error(f"Getting Error while parsing matches with crawler: {self.name}, err: {e}")

    def parse_odds(self, response, match_obj):
        logging.info("Parsing odds")
        try:
            decoded_response = response.body.decode("utf-8")
            parsed_response = json.loads(decoded_response)
            markets = parsed_response["data"]
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
                    bet = Bet(**bet_dict)
                    bets.append(bet)
                except OpportunityNotSupported:
                    # I can also implement some functionality, for example that if the the opportunity is not
                    # supported than I can collect them in DB and than explore them in browser without the need
                    # of finding it on the bookmaker site
                    continue
                
            match = match_obj
            match['bets'] = bets
            yield Match(**match)
            
        except Exception as e:
            logging.error(f"Getting Error while parsing odds with crawler: {self.name}, err: {e}")


    def err_back(self, failure):
        # log all failures
        logging.error(f"Getting Error while sending request with crawler: {self.name}, err: {repr(failure)}")

