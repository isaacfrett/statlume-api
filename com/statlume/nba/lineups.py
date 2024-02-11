import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from database import Database


def get_lineups():
    url = "https://www.rotowire.com/basketball/nba-lineups.php"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    boxes = soup.find_all(class_="lineup is-nba")

    lineups = {"Player": [], "Position": [], "Abbreviation": []}

    for box in boxes:
        teams = box.find_all("div", {"class": "lineup__abbr"})
        visitor = teams[0].text
        home = teams[1].text
        visitor_player_list = box.find("ul", {"class": "lineup__list is-visit"})
        visitor_players = visitor_player_list.find_all("li", limit=6)[1:6]
        for player in visitor_players:
            lineups["Player"].append(player.find("a")["title"])
            lineups["Position"].append(player.find("div").text)
            lineups["Abbreviation"].append(visitor)

        home_player_list = box.find("ul", {"class": "lineup__list is-home"})
        home_players = home_player_list.find_all("li", limit=6)[1:6]
        for player in home_players:
            lineups["Player"].append(player.find("a")["title"])
            lineups["Position"].append(player.find("div").text)
            lineups["Abbreviation"].append(home)

    df = pd.DataFrame(lineups, columns=["Player", "Abbreviation", "Position"])
    today = datetime.datetime.today().date()
    df["GameDate"] = pd.to_datetime(today)
    Database("nba").update_table("lineups", df)


def delete_lineups():
    Database("nba").drop_table("lineups")


def get_matchups() -> pd.DataFrame:
    lineups = Database("nba").select_table_as_df("lineups")
    teams = Database("nba").select_table_as_df("teams")
    todays_games = Database("nba").get_todays_games()

    lineups["Team"] = None
    lineups["VisitorPlayer"] = None
    lineups["HomePlayer"] = None
    lineups["VisitorTeam"] = None
    lineups["HomeTeam"] = None

    for index, player in lineups.iterrows():
        abv = player["Abbreviation"]
        if abv in teams["abbreviation"].values:
            match: str = teams.loc[teams["abbreviation"] == abv, "full_name"].values[0]
            lineups.at[index, "Team"] = match

    for index, player in lineups.iterrows():
        team = player["Team"]
        if team in todays_games["Home"].values:
            home: str = todays_games.loc[todays_games["Home"] == team, "Home"].values[0]
            visitor: str = todays_games.loc[
                todays_games["Home"] == home, "Visitor"
            ].values[0]
            lineups.at[index, "HomeTeam"] = home
            lineups.at[index, "VisitorTeam"] = visitor
        if team in todays_games["Visitor"].values:
            visitor = todays_games.loc[todays_games["Visitor"] == team, "Visitor"].values[
                0
            ]
            home = todays_games.loc[todays_games["Visitor"] == visitor, "Home"].values[0]
            lineups.at[index, "HomeTeam"] = home
            lineups.at[index, "VisitorTeam"] = visitor

    for index, player in lineups.iterrows():
        if player["Team"] == player["HomeTeam"]:
            lineups.at[index, "HomePlayer"] = player["PlayerName"]
            for index2, player2 in lineups.iterrows():
                if (
                    player["VisitorTeam"] == player2["Team"]
                    and player["Position"] == player2["Position"]
                ):
                    lineups.at[index, "VisitorPlayer"] = player2["PlayerName"]
        if player["Team"] == player["VisitorTeam"]:
            lineups.at[index, "VisitorPlayer"] = player["PlayerName"]
            for index2, player2 in lineups.iterrows():
                if (
                    player["HomeTeam"] == player2["Team"]
                    and player["Position"] == player2["Position"]
                ):
                    lineups.at[index, "HomePlayer"] = player2["PlayerName"]

    lineups = lineups.drop(
        columns=["PlayerName", "Abbreviation", "Team"]
    ).drop_duplicates()
    return lineups


if __name__ == "__main__":
    delete_lineups()
    get_lineups()
