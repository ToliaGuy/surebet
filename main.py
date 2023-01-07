"""CLI of the application"""
from typing import List

import typer

from apiestas.api.app.models.enums import Sport
from apiestas.api.run_server import run_server
from apiestas.crawling.enums import Spiders, BetTypes

app = typer.Typer()


@app.command(
    help="Run the REST API to serve the collected matches and bets"
)
def api(port: int = 9000, reload: bool = False):
    run_server(app="apiestas.api.app.asgi:app", host="0.0.0.0", port=port, reload=reload, log_level="info")


@app.command(
    help="Run the crawlers that feeds the API"
)
def crawler(spiders: List[Spiders] = None, sport: List[Sport] = None, bet_type: List[BetTypes] = None):
    from apiestas.crawling.run import start_process
    start_process(spiders=spiders, sports=sport, bet_types=bet_type)



@app.command()
def surebets():
    from apiestas.surebets.main import main
    main()


if __name__ == "__main__":
    app()


