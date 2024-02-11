import time

import pandas as pd
from nba_api.stats.endpoints import (
    hustlestatsboxscore,
    leaguegamelog,
    playergamelog,
    playervsplayer,
)
from nba_api.stats.static import players as playersdb
from nba_api.stats.static import teams

from com.statlume.nba.database import Database


def get_player_ids():
    return [x.get("id") for x in playersdb.get_active_players()]


def get_games():
    df = pd.concat(
        leaguegamelog.LeagueGameLog(season=2023).get_data_frames()
    ).drop_duplicates()
    return df


def insert_teams():
    teams_ = teams.get_teams()
    df = pd.DataFrame(teams_)
    Database("nba").update_table("teams", df)


def insert_players():
    players = {
        "Player_ID": [],
        "full_name": [],
    }

    for player in playersdb.get_active_players():
        players["Player_ID"].append(player["id"])
        players["full_name"].append(player["full_name"])

    Database("nba").update_table("players", players)


def insert_gamelogs():
    ids = get_player_ids()
    count = len(ids)
    db = Database("nba")
    for id in ids:
        print(str(count) + " player gamelogs remaining")
        count -= 1
        df = pd.concat(
            playergamelog.PlayerGameLog(player_id=id, season=2023).get_data_frames()
        )
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"], format="%b %d, %Y")
        matchup = {"Home": [], "Away": []}
        for index, row in df.iterrows():
            if "@" in row["MATCHUP"]:
                away, home = row["MATCHUP"].split(" @ ")
                matchup["Home"].append(home)
                matchup["Away"].append(away)
            if "vs." in row["MATCHUP"]:
                home, away = row["MATCHUP"].split(" vs. ")
                matchup["Home"].append(home)
                matchup["Away"].append(away)
        df = df.assign(**matchup)
        df.drop("MATCHUP", axis=1, inplace=True)
        db.update_table("gamelogs", df)
        time.sleep(1)


def insert_hustlestats():
    df = get_games()[["GAME_ID", "GAME_DATE"]]
    ids = df["GAME_ID"]
    count = len(ids)
    db = Database("nba")
    for index, row in df.iterrows():
        print(str(count) + " hustle stats remaining")
        count -= 1
        df1 = pd.concat(
            hustlestatsboxscore.HustleStatsBoxScore(
                game_id=row["GAME_ID"]
            ).get_data_frames()
        )
        df1["GAME_DATE"] = row["GAME_DATE"]
        db.update_table("hustlestats", df1)
        time.sleep(1)


def get_player_comparison(player_id, vs_player_id, date, seven, games: int = None):
    if games:
        df = playervsplayer.PlayerVsPlayer(
            player_id=player_id,
            vs_player_id=vs_player_id,
            date_from_nullable=seven,
            date_to_nullable=date,
            last_n_games=games,
        ).overall.get_data_frame()
        return df
    df = playervsplayer.PlayerVsPlayer(
        player_id=player_id,
        vs_player_id=vs_player_id,
        date_from_nullable=seven,
        date_to_nullable=date,
    ).overall.get_data_frame()
    return df


if __name__ == "__main__":
    Database("nba").drop_table("teams")
    Database("nba").drop_table("players")
    Database("nba").drop_table("gamelogs")
    insert_teams()
    insert_players()
    insert_gamelogs()
