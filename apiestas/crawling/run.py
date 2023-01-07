"""Launch the crawlers every CRAWLING_INTERVAL seconds (5 minutes by default)"""
import os
import sys
import logging
from typing import List

from capiestas.crawling.enums import Spiders
from capiestas.metrics_settings import PROMETHEUS_ENABLED
from capiestas import metrics

sys.path.insert(0, '..')

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import deferLater

from capiestas.crawling.spiders import ThunderPickSpider, N_OneBetSpider, TrustDiceWinSpider, DuelbitsSpider

CRAWLING_INTERVAL = int(os.getenv('CRAWLING_INTERVAL', 300))
CRAWLERS = {
    Spiders.TRUSTDICE_WIN: TrustDiceWinSpider,
    Spiders.N_ONE_BET: N_OneBetSpider,
    Spiders.DUELBITS: DuelbitsSpider,
    Spiders.THUNDER_PICK: ThunderPickSpider,
}


def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)


def crash(failure):
    logging.error(failure.getTraceback())


def start_sequentially(process: CrawlerProcess, spiders: List[Spiders], crawlers: list, **kwargs):
    if not crawlers:
        crawlers = get_crawlers(spiders)
    logging.info('Starting crawler {}'.format(crawlers[0].__name__))
    deferred = process.crawl(crawlers[0], **kwargs)
    deferred.addErrback(crash)
    if len(crawlers) > 1:
        deferred.addCallback(lambda _: start_sequentially(process, spiders, crawlers[1:], **kwargs))
    else:
        deferred.addCallback(lambda results:
                             logging.info(f"Finished all crawlers. "
                                          f"Waiting {CRAWLING_INTERVAL} seconds to start a new crawling process"))
        deferred.addCallback(sleep, seconds=CRAWLING_INTERVAL)
        deferred.addCallback(lambda _: start_sequentially(process, spiders, None, **kwargs))


def start_process(spiders: List[Spiders] = None, **kwargs):
    if PROMETHEUS_ENABLED:
        metrics.start_metrics_server()

    process = CrawlerProcess(settings=get_project_settings())
    start_sequentially(process, spiders,  crawlers=None, **kwargs)
    process.start()


def get_crawlers(spiders: List[Spiders]) -> list:
    # gets spider from typer application as arguments or if there is none than get crawlers from CRAWLER dictionary
    # which in there is only one so it is basically, set crawlers, that you want and if not there are default crawlers that will run
    # so in this way there doesnt need to be one program running all crawler, cause it can be too intensive depending on how much crawlers I have
    # so in docker I can just set how many crawlers do I want to assign to each container and have them run in distributed fashion
    return [CRAWLERS[spider] for spider in spiders] or list(CRAWLERS.values())


if __name__ == '__main__':
    start_process()