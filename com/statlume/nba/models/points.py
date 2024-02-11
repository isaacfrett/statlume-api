import datetime

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.discriminant_analysis import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
from sqlalchemy import text as sql_text

from com.statlume.nba.database import Database
from com.statlume.nba.logs import get_player_comparison

engine = create_engine(
    "mysql://" + "root" + ":" + "root" + "@" + "127.0.0.1" + "/" + "nba",
    pool_size=20,
    max_overflow=15,
    pool_timeout=10,
)


def get_recent_stats(data: pd.DataFrame):
    today = datetime.datetime.today()
    past_week = today - datetime.timedelta(days=7)
    df = pd.DataFrame()

    for i in data.index:
        id = data["Player_ID"][i]
        sql = """
            SELECT gamelogs.FGM, gamelogs.FGA, gamelogs.FG_PCT, gamelogs.FG3M, gamelogs.FG3A, gamelogs.FG3_PCT, gamelogs.MIN, gamelogs.PTS
            FROM gamelogs
            WHERE gamelogs.Player_ID = '%s' AND gamelogs.GAME_DATE > '%s'
        """ % (
            id,
            past_week,
        )
        dataframe = pd.read_sql(sql=sql_text(sql), con=engine.connect())
        column_means = dataframe.mean().fillna(0)
        mean_df = pd.DataFrame(column_means)
        data1 = pd.concat([data.iloc[i], mean_df], axis=0).T
        df = pd.concat([df, data1], ignore_index=True)

    return df


def gamelog_run():
    today = datetime.datetime.today()
    end_date = today - datetime.timedelta(days=90)

    sql = """
        SELECT players.full_name, gamelogs.GAME_DATE, gamelogs.FGM, gamelogs.FGA, gamelogs.FG_PCT, gamelogs.FG3M, gamelogs.FG3A, gamelogs.FG3_PCT, gamelogs.MIN, gamelogs.PTS
        FROM players
        INNER JOIN gamelogs ON gamelogs.Player_ID = players.Player_ID
        WHERE gamelogs.GAME_DATE > '%s'
    """ % (
        end_date
    )

    data = pd.read_sql(sql=sql_text(sql), con=engine.connect())

    features = ["FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "MIN"]

    x = data[features].values
    y = data["PTS"].values

    X_train, X_test, Y_train, Y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Dense(8, activation="relu", input_shape=(X_train.shape[1],)),
            tf.keras.layers.Dense(4, activation="relu"),
            tf.keras.layers.Dense(1),
        ]
    )

    model.compile(optimizer="adam", loss="mean_squared_error", metrics="accuracy")

    model.fit(X_train, Y_train, epochs=100, batch_size=32)

    loss, accuracy = model.evaluate(X_test, Y_test)
    print(f"Test Loss: {loss}")
    print(f"Test Accuracy: {100 * accuracy:.2f}")

    features = ["FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "MIN"]

    yesterday = today - datetime.timedelta(days=1)

    sql = """
        SELECT schedule.GameDate, teams.full_name, playerstats.FullName, players.Player_ID
        FROM players
        INNER JOIN playerstats ON playerstats.FullName = players.full_name
        INNER JOIN teams ON teams.id = playerstats.TeamID
        INNER JOIN schedule ON schedule.Home = teams.full_name
        WHERE schedule.GameDate > '%s' and schedule.GameDate < '%s'
    """ % (
        yesterday,
        today,
    )

    sql2 = """
        SELECT schedule.GameDate, teams.full_name, playerstats.FullName, players.Player_ID
        FROM players
        INNER JOIN playerstats ON playerstats.FullName = players.full_name
        INNER JOIN teams ON teams.id = playerstats.TeamID
        INNER JOIN schedule ON schedule.Visitor = teams.full_name
        WHERE schedule.GameDate > '%s' and schedule.GameDate < '%s'
    """ % (
        yesterday,
        today,
    )

    data1 = pd.read_sql(sql=sql_text(sql), con=engine.connect()).drop_duplicates()
    data2 = pd.read_sql(sql=sql_text(sql2), con=engine.connect()).drop_duplicates()
    data3 = pd.concat([data1, data2], ignore_index=True)
    df = get_recent_stats(data3)

    data = df[features].values

    data = scaler.transform(data)

    X = np.asarray(data).astype(np.float32)

    predictions = model.predict(X)
    result_df = df.copy()
    result_df["Predictions"] = predictions
    df = pd.DataFrame()
    for index, row in result_df.iterrows():
        if 15 < row["PTS"] < (row["Predictions"] - 0.5):
            data1 = pd.DataFrame(row).T
            df = pd.concat([df, data1], axis=0, ignore_index=True)

    print(df.sort_values(by=["full_name"]))


def feature_importance(X_train, Y_train):
    model = RandomForestClassifier()
    model.fit(X_train, Y_train)
    feature_importances = model.feature_importances_
    feature_importance_map = dict(zip(X_train.columns, feature_importances))
    sorted_features = sorted(
        feature_importance_map.items(), key=lambda x: x[1], reverse=True
    )
    for feature, importance in sorted_features:
        print(f"Feature: {feature}, Importance: {importance}")


def get_todays_games() -> pd.DataFrame:
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    sql = (
        "SELECT * FROM schedule WHERE schedule.GameDate > '%s' and schedule.GameDate < '%s';"
        % (yesterday, today)
    )
    todays_games = Database("nba").select_table_as_df("schedule", sql=sql)
    return todays_games


def get_recent_stats(player_id: str, logs: pd.DataFrame, field: str):
    player_logs = logs[logs["Player_ID"] == player_id]
    recent_three = player_logs.sort_values(by="GAME_DATE", ascending=False).head(3)
    average_value = recent_three[field].mean()
    return round(average_value, 1)


# def get_matchups():
#     games = get_todays_games()
#     teamstats = Database("nba").select_table_as_df("teamstats")
#     playerstats = Database("nba").select_table_as_df("playerstats")
#     gamelogs = Database("nba").select_table_as_df("gamelogs")

#     for index, row in games.iterrows():
#         date = row['GameDate']
#         date = str(date.strftime("%m-%d-%Y"))
#         home_team = row['Home']
#         visitor_team = row['Visitor']
#         home = teamstats[teamstats['TeamName'] == home_team]
#         visitor = teamstats[teamstats['TeamName'] == visitor_team]
#         home_player_stats = playerstats[playerstats['TeamName'] == home_team]
#         visitor_player_stats = playerstats[playerstats['TeamName'] == visitor_team]

#         visitor_player_logs = pd.DataFrame()
#         for index, player in visitor_player_stats[0:6].iterrows():
#             id = int(player['Player_ID'])
#             visitor_player_logs = pd.concat([visitor_player_logs, gamelogs[gamelogs['Player_ID'] == id]])

#         home_player_logs = pd.DataFrame()
#         for index, player in home_player_stats[0:6].iterrows():
#             id = int(player['Player_ID'])
#             home_player_logs = pd.concat([home_player_logs, gamelogs[gamelogs['Player_ID'] == id]])


# Starting Lineups
# Filter out injuries or denote
# - Player vs Player
# - Player vs Team
# - Player Season Average
# - Player Last 3
# - Player Matchup Season Average Def
# - Player Matchup Last 3 Average Def


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


def get_player_id(name: str):
    players = Database("nba").select_table_as_df("players")
    for index, player in players.iterrows():
        if player["full_name"] == name:
            return player["Player_ID"]


def get_opposing_player(player_id: int, player_name, game):
    gamelogs = Database("nba").select_table_as_df("gamelogs")
    playerstats = Database("nba").select_table_as_df("playerstats")
    teams = Database("nba").select_table_as_df("teams")
    positions = Database("nba").select_table_as_df("positions")

    position = ""
    for index, player in positions.iterrows():
        if player["Player"] == player_name:
            position = player["Position"]

    team_id = ""
    for index, player in playerstats.iterrows():
        if player["FullName"] == player_name:
            team_id = player["TeamID"]

    abv = ""
    for index, team in teams.iterrows():
        if team["id"] == team_id:
            abv = team["abbreviation"]

    player_logs = gamelogs[gamelogs["Player_ID"] == player_id]
    opponent_abv = ""

    for index, game2 in player_logs.iterrows():
        if game2["Game_ID"] == game["Game_ID"]:
            if game["Home"] == abv:
                opponent_abv = game["Away"]
            if game["Away"] == abv:
                opponent_abv = game["Home"]

    oppoenent_team = ""
    for index, team in teams.iterrows():
        if team["abbreviation"] == opponent_abv:
            oppoenent_team = team["full_name"]

    vs_players = []
    for index, player in playerstats.iterrows():
        if player["TeamName"] == oppoenent_team:
            for index, player2 in positions.iterrows():
                if player2["Player"] == player["FullName"]:
                    if player2["Position"] == position:
                        vs_players.append(player2["Player"])

    vs_player_ids = []
    for vs in vs_players:
        for index, player in playerstats.iterrows():
            if vs == player["FullName"]:
                vs_player_ids.append(player["Player_ID"])

    if len(vs_player_ids) == 1:
        return vs_player_ids[0]

    if len(vs_player_ids) > 1:
        minsplayed = 0
        vs_player_id = None
        for id in vs_player_ids:
            for index, player in playerstats.iterrows():
                if player["Player_ID"] == id:
                    if player["MinutesPlayed"] > minsplayed:
                        minsplayed = player["MinutesPlayed"]
                        vs_player_id = player["Player_ID"]
        return vs_player_id


def get_last_gamelogs(player_id: int, game_date: datetime, last_n_games: int = 0):
    gamelogs = Database("nba").select_table_as_df("gamelogs")
    player_logs = gamelogs[gamelogs["Player_ID"] == player_id]

    df = pd.DataFrame()
    if last_n_games == 0:
        logs = player_logs[player_logs["GAME_DATE"] < game_date]
        df = pd.concat([df, logs])

    if last_n_games > 0:
        logs = player_logs[player_logs["GAME_DATE"] < game_date][0:last_n_games]
        df = pd.concat([df, logs])

    columns_to_keep = [
        "MIN",
        "FGM",
        "FGA",
        "FG_PCT",
        "FG3M",
        "FG3A",
        "FG3_PCT",
        "FTM",
        "FTA",
        "FT_PCT",
        "OREB",
        "DREB",
        "REB",
        "AST",
        "STL",
        "BLK",
        "TOV",
        "PF",
        "PTS",
        "PLUS_MINUS",
    ]

    df = df[columns_to_keep]
    df = df.mean(axis=1)
    df = df.to_frame().T
    df.reset_index(drop=True, inplace=True)

    return df


def test_data():
    gamelogs = Database("nba").select_table_as_df("gamelogs")
    players = Database("nba").select_table_as_df("players")
    df = pd.DataFrame()
    #  Sort gamelogs by date

    for index, player in players.iterrows():
        # get gamelogs of the player
        df = pd.DataFrame()
        player_logs: pd.DataFrame = gamelogs[gamelogs["Player_ID"] == player["Player_ID"]]
        player_logs = player_logs.sort_values(by="GAME_DATE")
        game_pointer = 3
        current_game = player_logs.loc[game_pointer]
        for index, game in player_logs.iterrows():
            player_pts = current_game["PTS"]
            game_date = current_game["GAME_DATE"]
            opponent = get_opposing_player(
                player_id=player["Player_ID"], player_name=player["full_name"], game=game
            )
            player_recent = get_last_gamelogs(
                player_id=player["Player_ID"], last_n_games=3, game_date=game_date
            )
            print(player_recent)
            opponent_recent = get_last_gamelogs(
                player_id=opponent, last_n_games=3, game_date=game_date
            )

            season_stats = get_last_gamelogs(player_id=player["Player_ID"])
            oop_season_stats = get_last_gamelogs(player_id=opponent)

            # season_stats = pd.concat(            season_stats = get_last_gamelogs(player_id=player["Player_ID"])
            # season_stats = season_stats.to_frame().T

            print(player_recent)
            print(season_stats)

            #  Combine all dfs to one

            df = pd.concat([df])
            game_pointer += 1

    print(df)
    breakpoint()
    Database("nba").update_table("testingdata")

    # Query and combine from gamelogs for every game and the past three games from that date

    # Split data, test, train, save model


def predict_data():
    matchups = get_matchups()
    injuries = Database("nba").select_table_as_df("injuries")
    playerstats = Database("nba").select_table_as_df("playerstats")
    gamelogs = Database("nba").select_table_as_df("gamelogs")

    for index, matchup in matchups.iterrows():
        home_player_id = get_player_id(matchup["HomePlayer"])
        visitor_player_id = get_player_id(matchup["VisitorPlayer"])
        last_3_stats = get_player_comparison(
            player_id=home_player_id, vs_player_id=visitor_player_id, games=3
        )
        season_stats = get_player_comparison(
            player_id=home_player_id, vs_player_id=visitor_player_id
        )

        #  combine dfs

        #  load model and get predictions

    # For every matchup get the player vs player df
    # With each dataframe


if __name__ == "__main__":
    test_data()
