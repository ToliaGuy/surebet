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


class FortuneJackSpider(scrapy.Spider):

    # Attributes
    name = Spiders.FORTUNE_JACK.value
    rotate_user_agent = False


    def __init__(self, sports: List[Sport] = None, bet_types: List[BetTypes] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.sports = self._get_sport_names(sports) if sports else None
        self.bet_types = [bet_type.value for bet_type in bet_types] if bet_types else None
        self.tournament_urls = {}
        self.bookmakers_data = {}
        self.scope_ids = {}
        self.globals = {}
        