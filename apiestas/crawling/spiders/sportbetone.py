import logging
from typing import List

import scrapy

import re
import json

from capiestas.crawling.items import Match, Bet
from capiestas.crawling.enums import Spiders, BetTypes
from capiestas.api.app.models.enums import Sport


class SportBetOneSpider(scrapy.Spider):
    name = Spiders.SPORT_BET_ONE.value
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    

    def __init__(self, sports: List[Sport] = None, bet_types: List[BetTypes] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.main_url = "https://sportbet.one/"
        self.sports = None
        self.sport_urls = ["soccer"]
        self.bet_types = None
        self.tournament_urls = {}
        self.bookmakers_data = {}
        self.scope_ids = {}
        self.globals = {}
        
    
    def start_requests(self):
        logging.info("Getting tournaments for all of the sports")
        for sport_url in self.sport_urls:
            yield scrapy.Request(url=f"{self.main_url}sports/{sport_url}", callback=self.parse_tournaments,
                                errback=self.err_back, headers={'User-Agent': self.user_agent}, dont_filter=True,
                                cb_kwargs=dict(sport_url=sport_url))
    
    def parse_tournaments(self, response, sport_url):
        logging.info("Parsing tournaments")
        try:
            res_body = response.body.decode("utf-8")
            json_info = re.search(r'__REDUX_STATE__=(.*?)<\/script>', res_body).group(1)
            parsed_info = json.loads(json_info)
            league_ids = list(parsed_info["leagues"]["byId"].keys())
            for league_id in league_ids:
                league = parsed_info["leagues"]["byId"][league_id]
                yield scrapy.Request(url=f"{self.main_url}sports/{sport_url}/{league['slug']}", callback=self.parse_matches,
                                    errback=self.err_back, headers={'User-Agent': self.user_agent}, dont_filter=True,
                                    cb_kwargs=dict(sport_url=sport_url, league_url=league['slug']))

            # parse matches and than odds
        except Exception as e:
            logging.error(f"Getting Error while parsing tournaments with crawler: {self.name}, err: {e}")

    def parse_matches(self, response, sport_url, league_url):
        logging.info("Parsing matches")
        try:
            res_body = response.body.decode("utf-8")
            json_info = re.search(r'__REDUX_STATE__=(.*?)<\/script>', res_body).group(1)
            parsed_info = json.loads(json_info)
            match_ids = list(parsed_info["events"]["byId"].keys())
            for match_id in match_ids:
                match = parsed_info["events"]["byId"][match_id]
                # when match is not available it can trow an error of non-200-response
                yield scrapy.Request(url=f"{self.main_url}sports/{sport_url}/{league_url}/{match['slug']}", callback=self.parse_odds,
                                    errback=self.err_back, headers={'User-Agent': self.user_agent}, dont_filter=True,
                                    cb_kwargs=dict(sport_url=sport_url, league_url=league_url, match_url=match['slug']))

        except Exception as e:
            logging.error(f"Getting Error while parsing matches with crawler: {self.name}, err: {e}")

    def parse_odds(self, response, sport_url, league_url, match_url):
        logging.info("Parsing odds")
        try:
            res_body = response.body.decode("utf-8")
            json_info = re.search(r'__REDUX_STATE__=(.*?)<\/script>', res_body).group(1)
            parsed_info = json.loads(json_info)
            event_id = list(parsed_info["events"]["byId"].keys())[0]
            event = parsed_info["events"]["byId"]["event_id"]

        except Exception as e:
            logging.error(f"Getting Error while parsing odds with crawler: {self.name}, err: {e}")
        

    def err_back(self, failure):
        # log all failures
        logging.error(f"Getting Error while sending request with crawler: {self.name}, err: {repr(failure)}")