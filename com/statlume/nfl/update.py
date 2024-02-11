import datetime
import re
import time

import requests
from bs4 import BeautifulSoup
from database import Database
from requests import Response

teams = [
    "buf",
    "mia",
    "nwe",
    "nyj",
    "phi",
    "dal",
    "was",
    "nyg",
    "rav",
    "cle",
    "pit",
    "cin",
    "det",
    "gnb",
    "min",
    "chi",
    "clt",
    "htx",
    "oti",
    "jax",
    "sdg",
    "kan",
    "rai",
    "den",
    "nor",
    "car",
    "tam",
    "atl",
    "crd",
    "sea",
    "ram",
    "sfo",
]


def get_team_data(team: str) -> Response:
    url = "https://www.pro-football-reference.com/teams/"
    year = "/2023"
    return requests.get(url + team + year + ".htm")


def get_defense_data() -> Response:
    url = "https://www.pro-football-reference.com/years/"
    year = "/2023"
    return requests.get(url + year + "/opp.htm")


def get_schedule() -> Response:
    url = "https://www.pro-football-reference.com/years/"
    year = "/2023"
    return requests.get(url + year + "/games.htm")


def remove_comments(response: Response) -> BeautifulSoup:
    comment = re.compile("<!--|-->")
    soupdata = BeautifulSoup(comment.sub("", response.text), "html.parser")
    return soupdata


def insert_schedule(schedule: BeautifulSoup):
    tables = schedule.find_all("table")
    tbody = tables[0].find("tbody")
    trs = tbody.find_all("tr")

    schedule = {"GameDate": [], "HomeID": [], "Home": [], "VisitorID": [], "Visitor": []}

    for row in trs:
        if row.find("th", {"aria-label": "Week"}):
            continue
        game_date = row.find("td", {"data-stat": "game_date"}).text
        home = row.find("td", {"data-stat": "winner"}).text
        visitor = row.find("td", {"data-stat": "loser"}).text
        homeID = Database.select_team_id(home)
        visitorID = Database.select_team_id(visitor)

        schedule["GameDate"].append(game_date)
        schedule["HomeID"].append(homeID)
        schedule["Home"].append(home)
        schedule["VisitorID"].append(visitorID)
        schedule["Visitor"].append(visitor)

    Database.update_table("schedule", schedule)


def insert_defense(defense_data: BeautifulSoup):
    tables = defense_data.find_all("table")
    tbody = tables[0].find("tbody")
    trs = tbody.find_all("tr")

    defense_stats = {
        "TeamID": [],
        "TeamName": [],
        "Games_Played": [],
        "Pass_YPG": [],
        "Pass_YPA": [],
        "Rush_YPG": [],
        "Rush_YPA": [],
    }

    for row in trs:
        teamName = row.find("a").text
        teamID = Database.select_team_id(teamName)
        gp = float(row.find("td", {"data-stat": "g"}).text)
        p_yds = float(row.find("td", {"data-stat": "pass_yds"}).text)
        pnypa = float(row.find("td", {"data-stat": "pass_net_yds_per_att"}).text)
        r_yds = float(row.find("td", {"data-stat": "rush_yds"}).text)
        rnypa = float(row.find("td", {"data-stat": "rush_yds_per_att"}).text)

        defense_stats["TeamID"].append(teamID)
        defense_stats["TeamName"].append(teamName)
        defense_stats["Games_Played"].append(gp)
        defense_stats["Pass_YPG"].append(p_yds / gp)
        defense_stats["Pass_YPA"].append(pnypa)
        defense_stats["Rush_YPG"].append(r_yds / gp)
        defense_stats["Rush_YPA"].append(rnypa)

    Database.update_table("defensestats", defense_stats)


def insert_data(team: str, team_data: BeautifulSoup):
    tables = team_data.find_all("table")
    results = Database.select_team(team)
    teamid = results[0][0]
    teamName = results[0][1]
    trs = tables[1].find_all("tr")

    offense = {
        "TeamID": [teamid],
        "TeamName": [teamName],
        "Points_For": [trs[2].find("td", {"data-stat": "points"}).text],
        "1st_Downs": [trs[2].find("td", {"data-stat": "first_down"}).text],
        "Passing_Yards": [trs[2].find("td", {"data-stat": "pass_yds"}).text],
        "Passing_TDs": [trs[2].find("td", {"data-stat": "pass_td"}).text],
        "Rushing_Yards": [trs[2].find("td", {"data-stat": "rush_yds"}).text],
        "Rushing_TDs": [trs[2].find("td", {"data-stat": "rush_td"}).text],
    }

    defense = {
        "TeamID": [teamid],
        "TeamName": [teamName],
        "Points_For": [trs[3].find("td", {"data-stat": "points"}).text],
        "1st_Downs": [trs[3].find("td", {"data-stat": "first_down"}).text],
        "Passing_Yards": [trs[3].find("td", {"data-stat": "pass_yds"}).text],
        "Passing_TDs": [trs[3].find("td", {"data-stat": "pass_td"}).text],
        "Rushing_Yards": [trs[3].find("td", {"data-stat": "rush_yds"}).text],
        "Rushing_TDs": [trs[3].find("td", {"data-stat": "rush_td"}).text],
    }

    tbody = tables[4].find("tbody")
    trs = tbody.find_all("tr")

    players = {
        "LastName": [],
        "FirstName": [],
        "Position": [],
        "TeamID": [],
        "TeamName": [],
        "Uniform": [],
    }

    for row in trs:
        name = str(row.find("a").text).split()
        players["LastName"].append(name[1])
        players["FirstName"].append(name[0])
        players["Position"].append(row.find("td", {"data-stat": "pos"}).text)
        players["TeamID"].append(teamid)
        players["TeamName"].append(teamName)
        players["Uniform"].append(
            int(row.find("th", {"data-stat": "uniform_number"}).text)
        )

    Database.update_table("players", players)

    passing = {
        "PlayerID": [],
        "FirstName": [],
        "LastName": [],
        "TeamID": [],
        "TeamName": [],
        "Games_Played": [],
        "Passing_Yards": [],
        "Passing_TDs": [],
        "Interceptions": [],
        "Passing_Yards_Per_Game": [],
        "Passing_TDs_Per_Game": [],
        "Rate": [],
        "Sacks": [],
    }

    for row in trs:
        number = int(row.find("th", {"data-stat": "uniform_number"}).text)
        player = Database.select_player(teamid, number)
        playerID = player[0][0]
        firstname = player[0][1]
        lastname = player[0][2]

        gp = int(row.find("td", {"data-stat": "g"}).text)
        p_yards = int(row.find("td", {"data-stat": "pass_yds"}).text)
        p_tds = int(row.find("td", {"data-stat": "pass_td"}).text)

        rate = row.find("td", {"data-stat": "pass_rating"}).text

        if not rate:
            rate = 0
        rate = float(rate)

        passing["PlayerID"].append(playerID)
        passing["FirstName"].append(firstname)
        passing["LastName"].append(lastname)
        passing["TeamID"].append(teamid)
        passing["TeamName"].append(teamName)
        passing["Games_Played"].append(gp)
        passing["Passing_Yards"].append(p_yards)
        passing["Passing_TDs"].append(p_tds)
        passing["Interceptions"].append(row.find("td", {"data-stat": "pass_int"}).text)
        passing["Passing_Yards_Per_Game"].append(p_yards / gp)
        passing["Passing_TDs_Per_Game"].append(p_tds / gp)
        passing["Rate"].append(rate)
        passing["Sacks"].append(row.find("td", {"data-stat": "pass_sacked"}).text)

    rushing = {
        "PlayerID": [],
        "FirstName": [],
        "LastName": [],
        "TeamID": [],
        "TeamName": [],
        "Games_Played": [],
        "Rushing_Yards": [],
        "Rushing_TDs": [],
        "Rushing_Attempts": [],
        "Rushing_Yards_Per_Game": [],
        "Rushing_TDs_Per_Game": [],
        "Rushing_Attempts_Per_Game": [],
    }

    receiving = {
        "PlayerID": [],
        "FirstName": [],
        "LastName": [],
        "TeamID": [],
        "TeamName": [],
        "Games_Played": [],
        "Targets": [],
        "Receptions": [],
        "Receiving_Yards": [],
        "Receiving_TDs": [],
        "Targets_Per_Game": [],
        "Receptions_Per_Game": [],
        "Receiving_Yards_Per_Game": [],
        "Receiving_TDs_Per_Game": [],
    }

    tbody = tables[5].find("tbody")
    trs = tbody.find_all("tr")

    for row in trs:
        name = str(row.find("a").text).split()
        number = int(row.find("th", {"data-stat": "uniform_number"}).text)

        if not number in players["Uniform"]:
            players2 = {
                "LastName": [],
                "FirstName": [],
                "Position": [],
                "TeamID": [],
                "TeamName": [],
                "Uniform": [],
            }

            players2["LastName"].append(name[1])
            players2["FirstName"].append(name[0])
            players2["Position"].append(row.find("td", {"data-stat": "pos"}).text)
            players2["TeamID"].append(teamid)
            players2["TeamName"].append(teamName)
            players2["Uniform"].append(number)
            Database.update_table("players", players2)

        player = Database.select_player(teamid, number)
        playerID = player[0][0]
        firstname = player[0][1]
        lastname = player[0][2]

        gp = int(row.find("td", {"data-stat": "g"}).text)

        rush_yards = row.find("td", {"data-stat": "rush_yds"}).text

        if not rush_yards:
            rush_yards = 0
        rush_yards = int(rush_yards)

        rush_tds = row.find("td", {"data-stat": "rush_td"}).text

        if not rush_tds:
            rush_tds = 0
        rush_tds = int(rush_tds)

        rush_att = row.find("td", {"data-stat": "rush_att"}).text

        if not rush_att:
            rush_att = 0
        rush_att = int(rush_att)

        rushing["PlayerID"].append(playerID)
        rushing["FirstName"].append(firstname)
        rushing["LastName"].append(lastname)
        rushing["TeamID"].append(teamid)
        rushing["TeamName"].append(teamName)
        rushing["Games_Played"].append(gp)
        rushing["Rushing_Yards"].append(rush_yards)
        rushing["Rushing_TDs"].append(rush_tds)
        rushing["Rushing_Attempts"].append(rush_att)
        rushing["Rushing_Yards_Per_Game"].append(rush_yards / gp)
        rushing["Rushing_TDs_Per_Game"].append(rush_tds / gp)
        rushing["Rushing_Attempts_Per_Game"].append(rush_att / gp)

        targets = row.find("td", {"data-stat": "targets"}).text

        if not targets:
            targets = 0
        targets = int(targets)

        receptions = row.find("td", {"data-stat": "rec"}).text

        if not receptions:
            receptions = 0
        receptions = int(receptions)

        rec_yards = row.find("td", {"data-stat": "rec_yds"}).text

        if not rec_yards:
            rec_yards = 0
        rec_yards = int(rec_yards)

        rec_tds = row.find("td", {"data-stat": "rec_td"}).text

        if not rec_tds:
            rec_tds = 0
        rec_tds = int(rec_tds)

        receiving["PlayerID"].append(playerID)
        receiving["FirstName"].append(firstname)
        receiving["LastName"].append(lastname)
        receiving["TeamID"].append(teamid)
        receiving["TeamName"].append(teamName)
        receiving["Games_Played"].append(gp)
        receiving["Targets"].append(targets)
        receiving["Receptions"].append(receptions)
        receiving["Receiving_Yards"].append(rec_yards)
        receiving["Receiving_TDs"].append(rec_tds)
        receiving["Targets_Per_Game"].append(targets / gp)
        receiving["Receptions_Per_Game"].append(receptions / gp)
        receiving["Receiving_Yards_Per_Game"].append(rec_yards / gp)
        receiving["Receiving_TDs_Per_Game"].append(rec_tds / gp)

    Database.update_table("offense", offense)
    Database.update_table("defense", defense)
    Database.update_table("passing", passing)
    Database.update_table("rushing", rushing)
    Database.update_table("receiving", receiving)
    # Database.update_table("injuries", injuries)


if __name__ == "__main__":
    Database.drop_tables()
    Database.create_tables()
    Database.insert_teams()

    schedule = get_schedule()
    schedule = remove_comments(schedule)
    insert_schedule(schedule)

    defense_data = get_defense_data()
    defense_data = remove_comments(defense_data)
    insert_defense(defense_data)

    for team in teams:
        team_data = get_team_data(team)
        team_data = remove_comments(team_data)
        insert_data(team, team_data)
        print(team + " complete")
        time.sleep(10)
