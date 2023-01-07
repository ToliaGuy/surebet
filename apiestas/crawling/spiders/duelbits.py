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
from ..utils.duelbits import handle_opportunities


class DuelbitsSpider(scrapy.Spider):
    name = Spiders.DUELBITS.value
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    download_delay = 0.25 # for testing purposes

    def __init__(self, sports: List[Sport] = None, bet_types: List[BetTypes] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.main_url = "https://ws.duelbits.com/betradar/"
        self.sports = None
        self.sport_params = [dict(sport="soccer", sport_url="sr:sport:1")]
        self.bet_types = None

    
    def start_requests(self):
        logging.info("Getting tournaments for all of the sports")
        for sport_param in self.sport_params:
            yield scrapy.Request(url=f"{self.main_url}sports/{sport_param['sport_url']}/tournaments?state=upcoming", callback=self.parse_tournaments,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(sport_param=sport_param), dont_filter=True)


    def parse_tournaments(self, response, sport_param):
        logging.info("Parsing tournaments")
        try:
            decoded_response = response.body.decode("utf-8")
            tournaments = json.loads(decoded_response)
            for tournament in tournaments:
                yield scrapy.Request(url=f"{self.main_url}tournaments/{tournament['id']}/events?state=upcoming&limit=150", callback=self.parse_matches,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(sport_param=sport_param), dont_filter=True)
        except Exception as e:
            logging.error(f"Getting Error while parsing tournaments with crawler: {self.name}, err: {e}")
    

    def parse_matches(self, response, sport_param):
        logging.info("Parsing matches")
        try:
            decoded_response = response.body.decode("utf-8")
            matches = json.loads(decoded_response)
            for match in matches:
                tournament = f"{match['tournament']['category']['name']} {match['tournament']['name']}"
                match_obj = {
                    "bookmaker": slugify(self.name),
                    "sport": sport_param['sport'],
                    "tournament": slugify(tournament),
                    "tournament_nice": tournament,
                    "country": match['tournament']['category']['name'],
                    "commence_time": int(datetime.strptime(match["startTime"].replace(".000", ""), "%Y-%m-%dT%H:%M:%S%z").timestamp()),
                    "teams": [match["competitors"][0]["name"], match["competitors"][1]["name"]],
                    "url": ""
                }
                yield scrapy.Request(url=f"{self.main_url}events/{match['id']}/markets", callback=self.parse_odds,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, cb_kwargs=dict(sport_param=sport_param, match_obj=match_obj), dont_filter=True)

        except Exception as e:
            logging.error(f"Getting Error while parsing matches with crawler: {self.name}, err: {e}")


    def parse_odds(self, response, sport_param, match_obj):
        logging.info("Parsing odds")
        try:
            decoded_response = response.body.decode("utf-8")
            markets = json.loads(decoded_response)
            bets = []
            # duelbits have different strucuture of markets
            # therefore we have double loop
            for market in markets:
                try:
                    handled_opportunities = handle_opportunities(market, match_obj["teams"])
                    for opp in handled_opportunities["opportunities"]:
                        bet_dict = {
                            "bookmaker": slugify(self.name),
                            "bookmaker_nice": self.name,
                            "is_back": True,
                            "bet_type": handled_opportunities["bet_type"],
                            "bet_scope": handled_opportunities["bet_scope"],
                            "bet_category": market["name"],
                            "handicap": opp["handicap"],
                            "url": "",
                            "feed": "",
                            "opportunities": opp["opportunities"]
                        }
                        logging.info(bet_dict)
                        # choose what information gets passed into the bet object
                        bet = Bet(**bet_dict)
                        bets.append(bet)
                    
                except OpportunityNotSupported:
                    pass
            match = match_obj
            match['bets'] = bets
            yield Match(**match)

        except Exception as e:
            logging.error(f"Getting Error while parsing odds with crawler: {self.name}, err: {e}")

    def err_back(self, failure):
            # log all failures
            logging.error(f"Getting Error while sending request with crawler: {self.name}, err: {repr(failure)}")
