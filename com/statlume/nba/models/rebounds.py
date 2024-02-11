from datetime import datetime, timedelta

import pandas as pd
import tensorflow as tf
from sklearn.discriminant_analysis import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
from sqlalchemy import text as sql_text


class Rebounds:
    engine = create_engine(
        "mysql://" + "root" + ":" + "root" + "@" + "127.0.0.1" + "/" + "nba",
        pool_size=20,
        max_overflow=15,
        pool_timeout=10,
    )

    def get_predictions(self):
        thirty_days = datetime.today() - timedelta(days=30)
        sql = """
            SELECT players.full_name, gamelogs.MIN, gamelogs.OREB, gamelogs.DREB, gamelogs.REB, gamelogs.BLK, hustlestats.OFF_BOXOUTS, hustlestats.DEF_BOXOUTS, hustlestats.BOX_OUT_PLAYER_REBS, hustlestats.BOX_OUTS
            FROM players
            INNER JOIN gamelogs ON gamelogs.Player_ID = players.Player_ID
            INNER JOIN hustlestats ON hustlestats.GAME_ID = gamelogs.Game_ID
            WHERE gamelogs.GAME_DATE > '%s'
        """ % (
            thirty_days
        )

        features = ["MIN", "OREB", "DREB"]
        data = pd.read_sql(sql=sql_text(sql), con=self.engine.connect()).fillna(0)

        x = data[features].values
        y = data["REB"].values

        X_train, X_test, Y_train, Y_test = train_test_split(
            x, y, test_size=0.2, random_state=42
        )

        self.feature_importance(data[features], y)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # model = tf.keras.Sequential([
        #     tf.keras.layers.Dense(8, activation='relu', input_shape=(X_train.shape[1],)),
        #     tf.keras.layers.Dense(4, activation='relu'),
        #     tf.keras.layers.Dense(1)
        # ])

    def feature_importance(self, x, y):
        model = RandomForestClassifier()
        model.fit(x, y)
        feature_importances = model.feature_importances_
        feature_importance_map = dict(zip(x.columns, feature_importances))
        sorted_features = sorted(
            feature_importance_map.items(), key=lambda x: x[1], reverse=True
        )
        for feature, importance in sorted_features:
            print(f"Feature: {feature}, Importance: {importance}")


if __name__ == "__main__":
    Rebounds().get_predictions()
