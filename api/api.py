import requests
from requests.auth import HTTPBasicAuth
from MusicGameBot import API_URL, API_USERNAME, API_PASSWORD
import os


class MusicGameBotAPI:
    def get_emoji_count_by_guild_id(
        self, guild_id: int, hour=720, user_id: int | None = None
    ):
        api_url = os.path.join(API_URL, "emoji", "usage-rank")
        query_params = {"guild_id": guild_id, "hour": hour, "user_id": user_id}
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.get(api_url, params=query_params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    def get_member_rank(self, guild_id: int, emoji: str, hour: int):
        api_url = os.path.join(API_URL, "emoji", "member-rank")
        query_params = {"guild_id": guild_id, "emoji": emoji, "hour": hour}
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.get(api_url, params=query_params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
