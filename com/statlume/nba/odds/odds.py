from typing import Generator, List
import pandas as pd

from requests import Response
from com.statlume.nba.database import Database
from com.statlume.nba.odds.models import Market, NBAEvent
from com.statlume.odds.odds import OddsAPI

def get_outcomes(markets: List[Market]) -> Generator[pd.DataFrame, None, None]:
    for market in markets:
        for outcome in market.outcomes:
            if outcome.name == "Over":
                data = {
                    "Prop": [market.key],
                    "Name": [outcome.description],
                    "Line": [outcome.point],
                    "Odds": [outcome.price]
                }
                df = pd.DataFrame(data=data)
                yield df
    

def get_markets(event: NBAEvent, book: str) -> List[Market]:
    for bookmaker in event.bookmakers:
        if bookmaker.key == book:
            return bookmaker.markets
    return []


def get_dataframe_from_odds(response: Response) -> pd.DataFrame:
    event = NBAEvent.from_dict(response.json())
    markets = get_markets(event=event, book="draftkings")
    outcomes = get_outcomes(markets=markets)
    df = pd.DataFrame()
    for outcome in outcomes:
        df = pd.concat([df, outcome])
    return df


def get_ids(response: Response) -> List[str]:
    return [event['id'] for event in response.json()]
        

def main() -> None:
    sport = "basketball_nba"
    markets = "player_points,player_rebounds,player_assists,player_threes"
    events = OddsAPI().get_event_id(sport=sport)
    ids = get_ids(events)
    
    dataframe = pd.DataFrame()
    for id in ids:
        odds = OddsAPI().get_event_odds(sport=sport, id=id, markets=markets)
        dataframe = pd.concat([dataframe, get_dataframe_from_odds(odds)])
    df = dataframe.drop_duplicates()
    Database('nba').update_table('odds', df) 
        
 


if __name__ == "__main__":
    Database('nba').drop_table('odds')
    main()