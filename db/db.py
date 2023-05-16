import sys

import mariadb
from mariadb import ConnectionPool

from MusicGameBot import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


class MusicGameBotDB:
    # _instance = None

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #         cls._instance._pool = ConnectionPool(
    #             host=DB_HOST,
    #             user=DB_USER,
    #             password=DB_PASSWORD,
    #             database=DB_NAME,
    #             pool_name="muiscgamebot_db_pool",
    #         )
    #     return cls._instance

    # def get_connection(self):
    #     return self._pool.get_connection()

    def get_connection(self) -> mariadb.Connection | None:
        try:
            conn = mariadb.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                # pool_name="muiscgamebot_db_pool",
            )
            return conn
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

    def get_join_channel(self, guild_id: int) -> int:
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT channel_id FROM join_channel WHERE guild_id=?",
            (guild_id,),
        )
        result = cur.fetchone()

        cur.close()
        conn.close()
        try:
            return result[0]
        except:
            return

    def update_join_channel(self, guild_id: int, channel_id: int) -> None:
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM join_channel WHERE guild_id=?",
            (guild_id,),
        )
        result = cur.fetchone()

        if result:
            cur.execute(
                "UPDATE join_channel SET channel_id=? WHERE guild_id=?",
                (channel_id, guild_id),
            )
            conn.commit()
        else:
            cur.execute(
                "INSERT INTO join_channel (guild_id, channel_id) VALUES (?, ?)",
                (guild_id, channel_id),
            )
            conn.commit()

        cur.close()
        conn.close()

    def add_message_to_queue(self, guild_id: int, text: str):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO message_queue (guild_id, message) VALUES (?, ?)",
            (guild_id, text),
        )
        conn.commit()

        cur.close()
        conn.close()

    def get_and_remove_oldest_message(self, guild_id: int) -> str | None:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, message FROM message_queue WHERE guild_id = ? ORDER BY created_at ASC LIMIT 1",
            (guild_id,),
        )

        row = cur.fetchone()
        if row is None:
            return
        oldest_message = row[1]
        if row is not None:
            cur.execute("DELETE FROM message_queue WHERE id = ?", (row[0],))
            conn.commit()

        cur.close()
        conn.close()
        return oldest_message

    def upsert_pronunciation(self, guild_id: int, word: str, pronunciation: str):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM dictionary WHERE guild_id=? AND word=?",
            (guild_id, word),
        )
        result = cur.fetchone()

        if result:
            cur.execute(
                "UPDATE dictionary SET pronunciation=? WHERE guild_id=? AND word=?",
                (pronunciation, guild_id, word),
            )
            conn.commit()
        else:
            cur.execute(
                "INSERT INTO dictionary (guild_id, word, pronunciation) VALUES (?, ?, ?)",
                (guild_id, word, pronunciation),
            )
            conn.commit()

        cur.close()
        conn.close()

    def delete_pronunciation(self, guild_id: int, word: str):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM dictionary WHERE guild_id=? AND word=?",
            (guild_id, word),
        )
        result = cur.fetchone()
        if result:
            id = result[0]
            cur.execute("DELETE FROM dictionary WHERE id=?", (id,))
            conn.commit()

            cur.close()
            conn.close()
            return True
        else:
            cur.close()
            conn.close()
            return False

    def get_all_words(self, guild_id: int, order_by_length=False) -> list[tuple]:
        conn = self.get_connection()
        cur = conn.cursor()

        if order_by_length == True:
            cur.execute(
                "SELECT word, pronunciation FROM dictionary WHERE guild_id=? ORDER BY CHAR_LENGTH(word) DESC",
                (guild_id,),
            )
        else:
            cur.execute(
                "SELECT word, pronunciation FROM dictionary WHERE guild_id=? ORDER BY word ASC",
                (guild_id,),
            )
        result = cur.fetchall()

        cur.close()
        conn.close()
        return result

    def add_emoji_use(
        self, guild_id: int, PartialEmoji_str: str, is_message: bool, is_reaction: bool
    ) -> None:
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO emoji_log (guild_id, PartialEmoji_str, is_message, is_reaction) VALUES (?, ?, ?, ?)",
            (guild_id, PartialEmoji_str, is_message, is_reaction),
        )
        conn.commit()

        cur.close()
        conn.close()

    def get_emoji_count_by_guild_id(self, guild_id: int, hour=720):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT PartialEmoji_str, COUNT(*) AS emoji_count FROM emoji_log WHERE guild_id=? AND used_at >= DATE_SUB(NOW(), INTERVAL ? HOUR) GROUP BY PartialEmoji_str ORDER BY emoji_count DESC",
            (
                guild_id,
                hour,
            ),
        )
        result = cur.fetchall()

        cur.close()
        conn.close()
        return result
