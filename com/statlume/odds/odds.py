import os
import requests
from requests import Response


class OddsAPI:
    api_key = os.environ.get("ODDS_API")
    host = "https://api.the-odds-api.com"
    regions = "us"
    odds_format = "american"

    def get_sports(self) -> Response:
        endpoint = f"/v4/sports/?apiKey={self.api_key}"
        response = requests.get(self.host + endpoint)
        return response

    def get_event_id(self, sport: str) -> Response:
        endpoint = (
            f"/v4/sports/{sport}/odds/?apiKey={self.api_key}&regions={self.regions}"
        )
        response = requests.get(self.host + endpoint)
        return response

    def get_event_odds(self, sport: str, id: str, markets: str) -> Response:
        endpoint = f"/v4/sports/{sport}/events/{id}/odds?apiKey={self.api_key}&regions={self.regions}&markets={markets}&oddsFormat={self.odds_format}"
        response = requests.get(self.host + endpoint)
        return response
