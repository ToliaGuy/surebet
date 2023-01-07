from datetime import datetime
from typing import Union

import pytz
import json
import logging
from urllib.parse import urlencode

from scrapy import Request

from . import settings as st
from .enums import Spiders


class ApiestasPipeline(object):

    def __init__(self, crawler):
        self.crawler = crawler
        self.api_endpoint = f"http://{st.APIESTAS_API_URL}/api/matches/"
        self.date_tz = pytz.timezone("Europe/Madrid")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        self.upsert_match(spider, item)
        return item

    def upsert_match(self, spider, item):
        body = self.get_apiestas_match(spider, item)
        req = Request(self.api_endpoint, callback=self.upsert_success_callback, method='PUT',
                      body=json.dumps(body), meta={'item': item}, errback=self.upsert_match_error_callback)
        self.crawler.engine.crawl(req, spider)

    def upsert_success_callback(self, response):
        logging.debug(json.loads(response.body))

    def upsert_match_error_callback(self, failure):
        logging.error(json.loads(failure.value.response.body))

    def get_apiestas_match(self, spider, item: dict):
        match = {
            'bookmaker': item['bookmaker'],
            'tournament': item['tournament'],
            'tournament_nice': item['tournament_nice'],
            'url': item['url'],
            'commence_time': self._get_apiestas_datetime(item['commence_time'])
                             if type(item['commence_time']) == str else item['commence_time'],
            "teams": item['teams'],
            "sport": item["sport"],
            "feed": spider.name,
            "bets": self.get_apiestas_bets(item.get("bets", []))
        }
        return match

    def get_apiestas_bets(self, item_bets:list) -> list:
        bets = []
        for bet in item_bets:
            if len(bet["opportunities"]) > 1:
                bet_dict = {
                        "bookmaker": bet["bookmaker"],
                        "bookmaker_nice": bet["bookmaker_nice"],
                        "is_back": bet["is_back"],
                        "bet_type": bet["bet_type"],
                        "bet_scope": bet["bet_scope"],
                        "bet_category": bet["bet_category"],
                        "handicap": bet["handicap"],
                        "url": bet["url"],
                        "feed": bet["feed"],
                        "opportunities": bet["opportunities"]
                    }
                bets.append(bet_dict)
        return bets

    def _get_apiestas_datetime(self, date: datetime, as_unix=False) -> Union[str, int]:
        utc_datetime = self.date_tz.localize(date, is_dst=None).astimezone(pytz.utc)
        if as_unix:
            return int(utc_datetime.timestamp())
        else:
            return utc_datetime.isoformat()

