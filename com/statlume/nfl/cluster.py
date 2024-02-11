import datetime

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine
from sqlalchemy import text as sql_text


def get_passing_matchups():
    engine = create_engine(
        "mysql://" + "root" + ":" + "root" + "@" + "127.0.0.1" + "/" + "nfl"
    )

    today = datetime.date.today()
    week_out = datetime.date.today() + datetime.timedelta(days=7)

    sql = """
        SELECT passing.FirstName, passing.LastName, passing.Rate, passing.Passing_Yards_Per_Game, schedule.Visitor, schedule.GameDate, defensestats.Pass_YPG, defensestats.Pass_YPA
        FROM players
        INNER JOIN passing ON passing.PlayerID = players.PlayerID
        INNER JOIN schedule ON schedule.HomeID = passing.TeamID
        INNER JOIN defensestats ON defensestats.TeamID = schedule.VisitorID
        WHERE players.position = 'QB' AND schedule.GameDate BETWEEN '%s' AND '%s';
    """ % (
        today,
        week_out,
    )

    sql2 = """
        SELECT passing.FirstName, passing.LastName, passing.Rate, passing.Passing_Yards_Per_Game, schedule.Home, schedule.GameDate, defensestats.Pass_YPG, defensestats.Pass_YPA
        FROM players
        INNER JOIN passing ON passing.PlayerID = players.PlayerID
        INNER JOIN schedule ON schedule.VisitorID = passing.TeamID
        INNER JOIN defensestats ON defensestats.TeamID = schedule.HomeID
        WHERE players.position = 'QB' AND schedule.GameDate BETWEEN '%s' AND '%s';
    """ % (
        today,
        week_out,
    )

    data1 = pd.read_sql(sql=sql_text(sql), con=engine.connect())
    data1 = data1.rename(columns={"Visitor": "Opponent"})
    data2 = pd.read_sql(sql=sql_text(sql2), con=engine.connect())
    data2 = data2.rename(columns={"Home": "Opponent"})

    frames = [data1, data2]

    data = pd.concat(frames)

    features = ["Rate", "Passing_Yards_Per_Game", "Pass_YPG", "Pass_YPA"]

    X = data[features]

    scaled_df = StandardScaler().fit_transform(X)

    model = KMeans(init="random", n_clusters=3, n_init=10, random_state=1)
    model.fit(scaled_df)

    data["cluster"] = model.labels_

    for i in range(3):
        print(data[data["cluster"] == i])


def get_rushing_matchups():
    engine = create_engine(
        "mysql://" + "root" + ":" + "root" + "@" + "127.0.0.1" + "/" + "nfl"
    )

    today = datetime.date.today()
    week_out = datetime.date.today() + datetime.timedelta(days=7)

    sql = """
        SELECT rushing.FirstName, rushing.LastName, rushing.Rushing_Attempts_Per_Game, rushing.Rushing_Yards_Per_Game, schedule.Visitor, schedule.GameDate, defensestats.Rush_YPG, defensestats.Rush_YPA
        FROM players
        INNER JOIN rushing ON rushing.PlayerID = players.PlayerID
        INNER JOIN schedule ON schedule.HomeID = rushing.TeamID
        INNER JOIN defensestats ON defensestats.TeamID = schedule.VisitorID
        WHERE players.position = 'RB' AND schedule.GameDate BETWEEN '%s' AND '%s';
    """ % (
        today,
        week_out,
    )

    sql2 = """
        SELECT rushing.FirstName, rushing.LastName, rushing.Rushing_Attempts_Per_Game, rushing.Rushing_Yards_Per_Game, schedule.Home, schedule.GameDate, defensestats.Rush_YPG, defensestats.Rush_YPA
        FROM players
        INNER JOIN rushing ON rushing.PlayerID = players.PlayerID
        INNER JOIN schedule ON schedule.VisitorID = rushing.TeamID
        INNER JOIN defensestats ON defensestats.TeamID = schedule.HomeID
        WHERE players.position = 'RB' AND schedule.GameDate BETWEEN '%s' AND '%s';
    """ % (
        today,
        week_out,
    )

    data1 = pd.read_sql(sql=sql_text(sql), con=engine.connect())
    data1 = data1.rename(columns={"Visitor": "Opponent"})
    data2 = pd.read_sql(sql=sql_text(sql2), con=engine.connect())
    data2 = data2.rename(columns={"Home": "Opponent"})

    frames = [data1, data2]

    data = pd.concat(frames)

    features = [
        "Rushing_Attempts_Per_Game",
        "Rushing_Yards_Per_Game",
        "Rush_YPG",
        "Rush_YPA",
    ]

    X = data[features]

    scaled_df = StandardScaler().fit_transform(X)

    model = KMeans(init="random", n_clusters=3, n_init=10, random_state=1)
    model.fit(scaled_df)

    data["cluster"] = model.labels_

    for i in range(3):
        print(data[data["cluster"] == i])


def get_receiving_matchups():
    engine = create_engine(
        "mysql://" + "root" + ":" + "root" + "@" + "127.0.0.1" + "/" + "nfl"
    )

    today = datetime.date.today()
    week_out = datetime.date.today() + datetime.timedelta(days=7)

    sql = """
        SELECT players.Position, receiving.FirstName, receiving.LastName, receiving.Targets_Per_Game, receiving.Receptions_Per_Game, receiving.Receiving_Yards_Per_Game, schedule.Visitor, schedule.GameDate, defensestats.Pass_YPG, defensestats.Pass_YPA
        FROM players
        INNER JOIN receiving ON receiving.PlayerID = players.PlayerID
        INNER JOIN schedule ON schedule.HomeID = receiving.TeamID
        INNER JOIN defensestats ON defensestats.TeamID = schedule.VisitorID
        WHERE players.position IN ('RB', 'WR', 'TE') AND schedule.GameDate BETWEEN '%s' AND '%s';
    """ % (
        today,
        week_out,
    )

    sql2 = """
        SELECT players.Position, receiving.FirstName, receiving.LastName, receiving.Targets_Per_Game, receiving.Receptions_Per_Game, receiving.Receiving_Yards_Per_Game, schedule.Home, schedule.GameDate, defensestats.Pass_YPG, defensestats.Pass_YPA
        FROM players
        INNER JOIN receiving ON receiving.PlayerID = players.PlayerID
        INNER JOIN schedule ON schedule.VisitorID = receiving.TeamID
        INNER JOIN defensestats ON defensestats.TeamID = schedule.HomeID
        WHERE players.position IN ('RB', 'WR', 'TE') AND schedule.GameDate BETWEEN '%s' AND '%s';
    """ % (
        today,
        week_out,
    )

    data1 = pd.read_sql(sql=sql_text(sql), con=engine.connect())
    data1 = data1.rename(columns={"Visitor": "Opponent"})
    data2 = pd.read_sql(sql=sql_text(sql2), con=engine.connect())
    data2 = data2.rename(columns={"Home": "Opponent"})

    frames = [data1, data2]

    data = pd.concat(frames)

    features = [
        "Targets_Per_Game",
        "Receptions_Per_Game",
        "Receiving_Yards_Per_Game",
        "Pass_YPG",
        "Pass_YPA",
    ]

    X = data[features]

    scaled_df = StandardScaler().fit_transform(X)

    model = KMeans(init="random", n_clusters=3, n_init=10, random_state=1)
    model.fit(scaled_df)

    data["cluster"] = model.labels_

    for i in range(3):
        print(data[data["cluster"] == i])


def test_clusters(df: pd.DataFrame):
    kmeans_kwargs = {
        "init": "random",
        "n_init": 10,
        "random_state": 1,
    }

    sse = []
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(df)
        sse.append(kmeans.inertia_)

    plt.plot(range(1, 11), sse)
    plt.xticks(range(1, 11))
    plt.xlabel("Number of Clusters")
    plt.ylabel("SSE")
    plt.show()


if __name__ == "__main__":
    get_passing_matchups()
    get_rushing_matchups()
    get_receiving_matchups()
