import json
import logging
from typing import List, Dict

from bs4 import BeautifulSoup
from galaxy.api.errors import UnknownBackendResponse
from galaxy.api.types import SubscriptionGame


logger = logging.getLogger(__name__)


class PSNGamesParser:

    _SUBSCRIBED_GAMES_PAGINATOR_CSS_CLASS = 'ems-sdk-strand-paginator'
    _SUBSCRIBED_GAMES_CSS_CLASS = 'ems-sdk-product-tile-link'
    _GAME_DATA_TAG = 'data-telemetry-meta'

    def parse(self, response) -> List[SubscriptionGame]:
        try:
            games = self._subscription_games(response)
        except NotFoundSubscriptionPaginator:
            raise UnknownBackendResponse(f"HTML TAG: {self._SUBSCRIBED_GAMES_PAGINATOR_CSS_CLASS} was not found in response.")
        else:
            return [
                SubscriptionGame(game_id=game['titleId'], game_title=game['name'])
                for game in games if game.get('name') and game.get('titleId') and not game['name'].startswith('PlayStation')
            ]

    def _subscription_games(self, response: str) -> List[Dict]:
        """Scrapes all PS Plus Monthly games from https://store.playstation.com/subscriptions"""

        parsed_html = BeautifulSoup(response, 'html.parser')
        paginator = parsed_html.find("div", class_=self._SUBSCRIBED_GAMES_PAGINATOR_CSS_CLASS)
        if not paginator:
            raise NotFoundSubscriptionPaginator
        logger.debug("HTML response slice of %s tag: \n%s" % (self._SUBSCRIBED_GAMES_PAGINATOR_CSS_CLASS, paginator.decode_contents()))
        games = paginator.find_all("a", class_=self._SUBSCRIBED_GAMES_CSS_CLASS)
        result = []
        for game in games:
            try:
                game_data = getattr(game, 'attrs', {}).get(self._GAME_DATA_TAG)
                result.append(json.loads(game_data))
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(e)
        return result


class NotFoundSubscriptionPaginator(Exception):
    pass
