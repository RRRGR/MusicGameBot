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

    def add_friend_code_game(self, game_title: str):
        api_url = os.path.join(API_URL, "friend-code", "game")
        data = {"game_title": game_title}
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.post(api_url, json=data)

        if response.status_code == 200:
            print("POST request was successful.")
            return True
        else:
            print(f"POST request failed with status code: {response.status_code}")
            return False

    def delete_friend_code_game(self, game_title: str):
        api_url = os.path.join(API_URL, "friend-code", "game")
        data = {"game_title": game_title}
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.delete(api_url, json=data)

        if response.status_code == 200:
            print("DELETE request was successful.")
            return True
        else:
            print(f"DELETE request failed with status code: {response.status_code}")
            return False

    def get_game_titles(self):
        api_url = os.path.join(API_URL, "friend-code", "games")
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.get(api_url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    def upsert_friend_code(self, user_id: int, game_title: str, friend_code: str):
        api_url = os.path.join(API_URL, "friend-code")
        data = {
            "user_id": user_id,
            "game_title": game_title,
            "friend_code": friend_code,
        }
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.put(api_url, json=data)

        if response.status_code == 200:
            print("PUT request was successful.")
            return True
        else:
            print(f"PUT request failed with status code: {response.status_code}")
            return False

    def delete_friend_code(self, user_id: int, game_title: str):
        api_url = os.path.join(API_URL, "friend-code")
        data = {
            "user_id": user_id,
            "game_title": game_title,
        }
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.delete(api_url, json=data)

        if response.status_code == 200:
            print("DELETE request was successful.")
            return True
        else:
            print(f"DELETE request failed with status code: {response.status_code}")
            return False

    def get_friend_code(self, user_id: int | None, game_title: str | None):
        api_url = os.path.join(API_URL, "friend-code")
        query_params = {"user_id": user_id, "game_title": game_title}
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.get(api_url, params=query_params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    def insert_message_log(self, guild_id: int, channel_id: int, user_id: int):
        api_url = os.path.join(API_URL, "message", "log")
        data = {"guild_id": guild_id, "channel_id": channel_id, "user_id": user_id}
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.post(api_url, json=data)

        if response.status_code == 200:
            print("POST request was successful.")
            return True
        else:
            print(f"POST request failed with status code: {response.status_code}")
            return False

    def get_message_count(
        self, guild_id: int, channel_id: int | None, user_id: int, hours: int
    ):
        api_url = os.path.join(API_URL, "message", "count")
        query_params = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "user_id": user_id,
            "hours": hours,
        }
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
        response = session.get(api_url, params=query_params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
