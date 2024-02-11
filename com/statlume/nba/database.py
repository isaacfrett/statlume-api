import datetime
from typing import Any, Dict, Optional, Union
from mysql.connector import MySQLConnection
from mysql.connector.cursor import CursorBase
import pandas as pd
from sqlalchemy import create_engine


class Database:

    name = None
    engine = create_engine('mysql://'+'root'+':'+'root'+'@'+'127.0.0.1'+'/'+'nba')

    def __init__(self, name: str) -> None:
        self.name = name

    def get_connection(self) -> MySQLConnection:
        connection: MySQLConnection = MySQLConnection(
            user='root',
            password='root',
            host='127.0.0.1',
            database=self.name
        )
        return connection      

    def drop_table(self, tablename: str):
        connection = self.get_connection()
        cursor: CursorBase = connection.cursor()
        sql = "DROP TABLE IF EXISTS %s;" % (tablename)
        cursor.execute(sql)
        cursor.close()
        connection.close()

    def select_abbreviations(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        sql = "SELECT abbreviation FROM teams;"
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results

    def select_teams(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        sql = "SELECT id, full_name, abbreviation FROM teams"
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    
    def select_player_id(self, name: str):
        connection = self.get_connection()
        cursor = connection.cursor()
        sql = 'SELECT Player_ID FROM players WHERE full_name = ("%s");' % (name)
        cursor.execute(sql)
        results = cursor.fetchone()
        cursor.close()
        connection.close()
        return results
    
    def select_player_name(self, id: int):
        connection = self.get_connection()
        cursor = connection.cursor()
        sql = 'SELECT full_name FROM players WHERE Player_ID = %s;' % (id)
        cursor.execute(sql)
        results = cursor.fetchone()
        cursor.close()
        connection.close()
        return results
    
    def select_team(self, team: str):
        connection = self.get_connection()
        cursor = connection.cursor()
        sql = "SELECT id, abbreviation FROM teams WHERE full_name = '%s';" % (team)
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    
    def select_table(self, table: str):
        connection = self.get_connection()
        cursor = connection.cursor()
        sql = "SELECT * FROM %s;" % (table)
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    
    def select_table_as_df(self, table: str, sql: Optional[str] = None) -> pd.DataFrame:
        connection = self.get_connection()
        cursor = connection.cursor()
        if not sql: 
            sql = "SELECT * FROM %s;" % (table)
        cursor.execute(sql)
        results = cursor.fetchall()
        if not cursor.description:
           raise Exception() 
        df = pd.DataFrame(results, columns=[col[0] for col in cursor.description])
        cursor.close()
        connection.close()
        return df
    
    def select_player_odds(self, player: str, field: str):
        connection = self.get_connection()
        cursor = connection.cursor()
        sql = "SELECT Line, Odds FROM odds WHERE odds.Name = '%s' and odds.Prop = '%s';" % (player, field)
        cursor.execute(sql)
        results = cursor.fetchone()
        cursor.close()
        connection.close()
        return results

    def get_todays_games(self) -> pd.DataFrame:
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        sql = "SELECT * FROM schedule WHERE schedule.GameDate > '%s' and schedule.GameDate < '%s';" % (yesterday, today)
        todays_games = self.select_table_as_df("schedule", sql=sql)
        return todays_games


    def update_table(self, table: str, data: Union[Dict[Any, Any], pd.DataFrame]) -> None:
        if isinstance(data, Dict):
            data = pd.DataFrame.from_dict(data)
        data.to_sql(con=self.engine, name=table, if_exists='append', index=False)