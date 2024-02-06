from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class Outcome():
    name: str
    description: str
    price: int
    point: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Outcome":
        return cls(
            name=data.get('name', str()),
            description=data.get('description', str()),
            price=data.get('price', int()),
            point=data.get('point', float())
        )

@dataclass(frozen=True)
class Market():
    key: str
    last_update: str
    outcomes: List[Outcome]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Market":
        return cls(
            key=data.get('key', str()),
            last_update=data.get('last_update', str()),
            outcomes=[Outcome.from_dict(out) for out in data.get("outcomes", [])]
        )


@dataclass(frozen=True)
class Bookmaker():
    key: str
    title: str
    markets: List[Market]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bookmaker":
        return cls(
            key=data.get('key', str()),
            title=data.get('title', str()),
            markets=[
                Market.from_dict(market) for market in data.get("markets", [])
            ]
        )

@dataclass(frozen=True)
class NBAEvent():
    id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str
    bookmakers: List[Bookmaker]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NBAEvent":
        return cls(
            id=data.get('id', str()),
            sport_key=data.get('sport_key', str()),
            sport_title=data.get('sport_title', str()),
            commence_time=data.get('commence_time', str()),
            home_team=data.get('home_team', str()),
            away_team=data.get('away_team', str()),
            bookmakers=[
                Bookmaker.from_dict(book) for book in data.get("bookmakers", [])
            ]
        )