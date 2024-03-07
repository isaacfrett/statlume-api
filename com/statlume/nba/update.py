import re
import time

import requests
from bs4 import BeautifulSoup
from database import Database
from requests import Response

abbreviations = [
    "BOS",
    "ORL",
    "MIL",
    "PHI",
    "IND",
    "NYK",
    "CLE",
    "MIA",
    "BRK",
    "ATL",
    "TOR",
    "CHI",
    "CHO",
    "WAS",
    "DET",
    "MIN",
    "OKC",
    "DAL",
    "DEN",
    "SAC",
    "LAL",
    "HOU",
    "LAC",
    "PHO",
    "NOP",
    "GSW",
    "UTA",
    "MEM",
    "POR",
    "SAS",
]


def get_team_data(team: str) -> Response:
    url = "https://www.basketball-reference.com/teams/"
    year = "2024"
    return requests.get(url + team + "/" + year + ".html")


def remove_comments(response: Response) -> BeautifulSoup:
    comment = re.compile("<!--|-->")
    soupdata = BeautifulSoup(comment.sub("", response.text), "html.parser")
    return soupdata


def insert_team_data(soup: BeautifulSoup):
    teamName = (
        soup.find("title").text.split("Roster")[0].split(" ", maxsplit=1)[1].strip()
    )
    team = Database("nba").select_team(teamName)
    id = team[0][0]
    abv = team[0][1]
    team_opp_table = soup.find("table", {"id": "team_and_opponent"})
    team_opp_body = team_opp_table.find("tbody")
    team_opp_row = team_opp_body.find_all("tr")
    misc_table = soup.find("table", {"id": "team_misc"})
    misc_body = misc_table.find("tbody")
    misc_row = misc_body.find_all("tr")

    team_stats = {
        "Team_ID": [id],
        "Team": [teamName],
        "Abbreviation": [abv],
        "FGPercent": [float(team_opp_row[1].find("td", {"data-stat": "fg_pct"}).text)],
        "3PPercent": [float(team_opp_row[1].find("td", {"data-stat": "fg3_pct"}).text)],
        "2PPercent": [float(team_opp_row[1].find("td", {"data-stat": "fg2_pct"}).text)],
        "FTPercent": [float(team_opp_row[1].find("td", {"data-stat": "ft_pct"}).text)],
        "OffReboundsPerGame": [
            float(team_opp_row[1].find("td", {"data-stat": "orb_per_g"}).text)
        ],
        "DefReboundsPerGame": [
            float(team_opp_row[1].find("td", {"data-stat": "drb_per_g"}).text)
        ],
        "ReboundsPerGame": [
            float(team_opp_row[1].find("td", {"data-stat": "trb_per_g"}).text)
        ],
        "AssistsPerGame": [
            float(team_opp_row[1].find("td", {"data-stat": "ast_per_g"}).text)
        ],
        "StealsPerGame": [
            float(team_opp_row[1].find("td", {"data-stat": "stl_per_g"}).text)
        ],
        "BlocksPerGame": [
            float(team_opp_row[1].find("td", {"data-stat": "blk_per_g"}).text)
        ],
        "TurnoversPerGame": [
            float(team_opp_row[1].find("td", {"data-stat": "tov_per_g"}).text)
        ],
        "PointsPerGame": [
            float(team_opp_row[1].find("td", {"data-stat": "pts_per_g"}).text)
        ],
        "OppFGPercent": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_fg_pct"}).text)
        ],
        "Opp3PPercent": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_fg3_pct"}).text)
        ],
        "Opp2PPercent": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_fg2_pct"}).text)
        ],
        "OppFTPercent": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_ft_pct"}).text)
        ],
        "OppOffReboundsPerGame": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_orb_per_g"}).text)
        ],
        "OppDefReboundsPerGame": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_drb_per_g"}).text)
        ],
        "OppReboundsPerGame": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_trb_per_g"}).text)
        ],
        "OppAssistsPerGame": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_ast_per_g"}).text)
        ],
        "OppStealsPerGame": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_stl_per_g"}).text)
        ],
        "OppBlocksPerGame": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_blk_per_g"}).text)
        ],
        "OppPointsPerGame": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_pts_per_g"}).text)
        ],
        "OppTurnoversPerGame": [
            float(team_opp_row[5].find("td", {"data-stat": "opp_tov_per_g"}).text)
        ],
        "StrengthOfSchedule": [float(misc_row[0].find("td", {"data-stat": "sos"}).text)],
        "OffRating": [float(misc_row[0].find("td", {"data-stat": "off_rtg"}).text)],
        "DefRating": [float(misc_row[0].find("td", {"data-stat": "def_rtg"}).text)],
        "Pace": [float(misc_row[0].find("td", {"data-stat": "pace"}).text)],
        "FTAttemptRate": [
            float(misc_row[0].find("td", {"data-stat": "fta_per_fga_pct"}).text)
        ],
        "3PAttemptRate": [
            float(misc_row[0].find("td", {"data-stat": "fg3a_per_fga_pct"}).text)
        ],
        "EffectiveFG": [float(misc_row[0].find("td", {"data-stat": "efg_pct"}).text)],
        "TurnoverPercent": [float(misc_row[0].find("td", {"data-stat": "tov_pct"}).text)],
        "OffReboundPercent": [
            float(misc_row[0].find("td", {"data-stat": "orb_pct"}).text)
        ],
        "FTPFG": [float(misc_row[0].find("td", {"data-stat": "ft_rate"}).text)],
        "OppEffectiveFG": [
            float(misc_row[0].find("td", {"data-stat": "opp_efg_pct"}).text)
        ],
        "OppTurnoverPercent": [
            float(misc_row[0].find("td", {"data-stat": "opp_tov_pct"}).text)
        ],
        "OppDefReboundPercent": [
            float(misc_row[0].find("td", {"data-stat": "drb_pct"}).text)
        ],
        "OppFTPFG": [float(misc_row[0].find("td", {"data-stat": "opp_ft_rate"}).text)],
        "PTS_RANK": [float(team_opp_row[6].find("td", {"data-stat": "opp_pts"}).text)],
        "2PP_RANK": [
            float(team_opp_row[6].find("td", {"data-stat": "opp_fg2_pct"}).text)
        ],
        "2P_RANK": [float(team_opp_row[6].find("td", {"data-stat": "opp_fg2"}).text)],
        "3PP_RANK": [
            float(team_opp_row[6].find("td", {"data-stat": "opp_fg3_pct"}).text)
        ],
        "3P_RANK": [float(team_opp_row[6].find("td", {"data-stat": "opp_fg3"}).text)],
        "OREB_RANK": [float(team_opp_row[6].find("td", {"data-stat": "opp_orb"}).text)],
        "DREB_RANK": [float(team_opp_row[6].find("td", {"data-stat": "opp_drb"}).text)],
        "REB_RANK": [float(team_opp_row[6].find("td", {"data-stat": "opp_trb"}).text)],
        "AST_RANK": [float(team_opp_row[6].find("td", {"data-stat": "opp_ast"}).text)],
    }

    Database("nba").update_table("teamstats", team_stats)


def insert_player_data(soup: BeautifulSoup):
    teamName = (
        soup.find("title").text.split("Roster")[0].split(" ", maxsplit=1)[1].strip()
    )
    player_table = soup.find("table", {"id": "per_game"})
    advanced = soup.find("table", {"id": "advanced"})
    roster = soup.find("table", {"id": "roster"})
    a_tbody = advanced.find("tbody")
    tbody = player_table.find("tbody")
    r_tbody = roster.find("tbody")
    a_trs = a_tbody.find_all("tr")
    trs = tbody.find_all("tr")
    r_trs = r_tbody.find_all("tr")
    team = Database("nba").select_team(teamName)
    id = team[0][0]

    player_stats = {
        "Player": [],
        "Player_ID": [],
        "Team_ID": [],
        "Team": [],
        "AGE": [],
        "MP": [],
        "PTS": [],
        "FG3M": [],
        "REB": [],
        "AST": [],
        "STL": [],
        "BLK": [],
        "TO": [],
        "FGA": [],
        "FG": [],
        "FGP": [],
        "EFG": [],
        "PER": [],
        "TSP": [],
        "3PR": [],
        "FTR": [],
        "USG": [],
    }

    for row in trs:
        name = row.find("td", {"data-stat": "player"}).text
        player_stats["Player"].append(name)
        player_id = Database("nba").select_player_id(name)
        if not player_id:
            player_id = 0
        player_stats["Player_ID"].append(player_id)
        player_stats["Team_ID"].append(id)
        player_stats["Team"].append(teamName)
        player_stats["AGE"].append(int(row.find("td", {"data-stat": "age"}).text))
        player_stats["MP"].append(float(row.find("td", {"data-stat": "mp_per_g"}).text))
        player_stats["PTS"].append(float(row.find("td", {"data-stat": "pts_per_g"}).text))
        player_stats["FG3M"].append(
            float(row.find("td", {"data-stat": "fg3_per_g"}).text)
        )
        player_stats["REB"].append(float(row.find("td", {"data-stat": "trb_per_g"}).text))
        player_stats["AST"].append(float(row.find("td", {"data-stat": "ast_per_g"}).text))
        player_stats["STL"].append(float(row.find("td", {"data-stat": "stl_per_g"}).text))
        player_stats["BLK"].append(float(row.find("td", {"data-stat": "blk_per_g"}).text))
        player_stats["TO"].append(float(row.find("td", {"data-stat": "tov_per_g"}).text))
        player_stats["FGA"].append(float(row.find("td", {"data-stat": "fga_per_g"}).text))
        player_stats["FG"].append(float(row.find("td", {"data-stat": "fg_per_g"}).text))
        fgper = row.find("td", {"data-stat": "fg_pct"}).text

        if not fgper:
            fgper = 0
        fgper = float(fgper)
        player_stats["FGP"].append(fgper)
        
        eFG = row.find("td", {"data-stat": "efg_pct"}).text
        if not eFG:
            eFG = 0
        eFG = float(eFG)
        player_stats["EFG"].append(eFG)

        for row2 in a_trs:
            name2 = row2.find("td", {"data-stat": "player"}).text
            if name == name2:
                per = row2.find("td", {"data-stat": "per"}).text
                if not per:
                    per = 0
                per = float(per)    
                player_stats["PER"].append(per)


                tsper = row2.find("td", {"data-stat": "ts_pct"}).text
                if not tsper:
                    tsper = 0
                tsper = float(tsper)
                player_stats["TSP"].append(tsper)

                threePAr = row2.find("td", {"data-stat": "fg3a_per_fga_pct"}).text
                if not threePAr:
                    threePAr = 0
                threePAr = float(threePAr)
                player_stats["3PR"].append(threePAr)

                fTr = row2.find("td", {"data-stat": "fta_per_fga_pct"}).text
                if not fTr:
                    fTr = 0
                fTr = float(fTr)
                player_stats["FTR"].append(fTr)

                usg = row2.find("td", {"data-stat": "usg_pct"}).text
                if not usg:
                    usg = 0
                usg = float(usg)
                player_stats["USG"].append(usg)

    positions = {"Player": [], "Position": []}

    for row in r_trs:
        positions["Player"].append(row.find("td", {"data-stat": "player"}).a.text)
        positions["Position"].append(row.find("td", {"data-stat": "pos"}).text)

    Database("nba").update_table("positions", positions)
    Database("nba").update_table("playerstats", player_stats)


def insert_injuries(soup: BeautifulSoup):
    try:
        injuries = soup.find("table", {"id": "injuries"})
        tbody = injuries.find("tbody")
        trs = tbody.find_all("tr")
    except:
        return

    injuries = {"Player": [], "Team": [], "Status": []}

    for row in trs:
        status: str = row.find("td", {"data-stat": "note"}).text
        first_word = status.split(" ")[0]
        if first_word == "Day":
            status = "DTD"
        if first_word == "Out":
            status = "O"
        if first_word == "Day":
            status = "DTD"

        injuries["Player"].append(row.find("th", {"data-stat": "player"}).text)
        injuries["Team"].append(row.find("td", {"data-stat": "team_name"}).text)
        injuries["Status"].append(status)

    Database("nba").update_table("injuries", injuries)


if __name__ == "__main__":
    Database("nba").drop_table("playerstats")
    Database("nba").drop_table("teamstats")
    Database("nba").drop_table("injuries")
    Database("nba").drop_table("positions")

    for team in abbreviations:
        team_data = get_team_data(team)
        team_data = remove_comments(team_data)
        insert_team_data(team_data)
        insert_player_data(team_data)
        insert_injuries(team_data)
        print(team + " complete")
        time.sleep(3)
