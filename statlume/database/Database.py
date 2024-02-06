from typing import Optional
import pandas as pd
import sqlalchemy


class Database:

    database_name = None

    def __init__(self, database_name: str) -> None:
        self.database_name = database_name

    def get_connection(self) -> sqlalchemy.Engine:
        user = 'root'
        password = 'root'
        host = '127.0.0.1'
        port = 3306
        database = self.database_name
        return sqlalchemy.create_engine(
            url="mysql://{0}:{1}@{2}:{3}/{4}".format(
                user, password, host, port, database
            )
        )    
    
    def get_player_stat(self, name: str):
        connection = self.get_connection()
        sql = "SELECT * FROM playerstats WHERE Player = '%s';" % (name)
        df = pd.read_sql(sql, connection)
        return df.to_dict(orient='list')
    
    def get_player_logs(self, id: int):
        connection = self.get_connection()
        sql = "SELECT * FROM gamelogs WHERE Player_ID = (%s);" % (id)
        df = pd.read_sql(sql, connection)
        return df.to_dict(orient='list')
    
    def get_player_logs_games(self, name: str, games: int):
        connection = self.get_connection()
        sql = """SELECT *
        FROM gamelogs 
        INNER JOIN players ON players.Player_ID = gamelogs.Player_ID
        WHERE players.full_name = '%s';""" % (name)
        df = pd.read_sql(sql, connection).head(games)
        df["GAME_DATE"] = df["GAME_DATE"].dt.strftime('%Y-%m-%d')
        return df.to_dict(orient='list')
    
    def get_teams(self):
        connection = self.get_connection()
        sql = "SELECT * FROM teams;"
        df = pd.read_sql(sql, connection)
        return df.to_dict(orient='list')
    
    def get_players(self, team: str):
        connection = self.get_connection()
        sql = """SELECT playerstats.Player
        FROM playerstats 
        INNER JOIN teams ON teams.id = playerstats.Team_ID
        WHERE teams.abbreviation = '%s';""" % (team) 
        df = pd.read_sql(sql, connection)
        return df.to_dict(orient='list')
    
    def get_odds(self, player: str, prop: str):
        connection = self.get_connection()
        sql = "SELECT * FROM odds WHERE Name = '%s' AND Prop = '%s';" % (player, prop) 
        df = pd.read_sql(sql, connection)
        return df.to_dict(orient='list')

