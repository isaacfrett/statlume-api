import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from database import Database
from requests import Response

months = ["october", "november", "december", "january", "february", "march", "april"]


def get_schedule(month: str) -> Response:
    url = "https://www.basketball-reference.com/leagues/NBA_"
    year = "2024"
    return requests.get(url + year + "_games-" + month + ".html")


def remove_comments(response: Response) -> BeautifulSoup:
    comment = re.compile("<!--|-->")
    soupdata = BeautifulSoup(comment.sub("", response.text), "html.parser")
    return soupdata


def insert_schedule(soup: BeautifulSoup):
    tables = soup.find_all("table")

    schedule = {"GameDate": [], "Home": [], "Visitor": []}

    for table in tables:
        tbody = table.find("tbody")
        trs = tbody.find_all("tr")

        for row in trs:
            game_date = str(row.find("a").text)
            game_date = game_date.split(",", maxsplit=1)[1]
            game_date = game_date.replace(",", "")
            game_date = datetime.strptime(game_date, " %b %d %Y")
            home = row.find("td", {"data-stat": "home_team_name"}).a.text
            visitor = row.find("td", {"data-stat": "visitor_team_name"}).a.text
            schedule["GameDate"].append(game_date)
            schedule["Home"].append(home)
            schedule["Visitor"].append(visitor)

    Database("nba").update_table("schedule", schedule)


if __name__ == "__main__":
    Database("nba").drop_table("schedule")

    for month in months:
        schedule = get_schedule(month)
        schedule = remove_comments(schedule)
        insert_schedule(schedule)
        print(month + " complete")
        time.sleep(10)
