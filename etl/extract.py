import os

import psycopg
import requests
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

load_dotenv()

USERNAME = os.environ.get("CHESS_USERNAME", "dz-1804")
BASE_URL = f"https://api.chess.com/pub/player/{USERNAME}/games"
HEADERS = {
    "User-Agent": "chess-insights/0.1 (portfolio project; github.com/zunigad1804-dot/chess-insights)"
}

INSERT_SQL = """
    INSERT INTO staging.raw_games (source, game_id, played_month, payload)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (source, game_id) DO NOTHING
"""


def connect():
    return psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )


def get_archives():
    r = requests.get(f"{BASE_URL}/archives", headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()["archives"]


def get_games(archive_url):
    r = requests.get(archive_url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()["games"]


def game_id(game_url):
    # https://www.chess.com/game/live/123 -> "live/123"
    return "/".join(game_url.rstrip("/").split("/")[-2:])


def save_games(conn, games, month):
    rows = [("chesscom", game_id(g["url"]), month, Jsonb(g)) for g in games]
    with conn.cursor() as cur:
        cur.executemany(INSERT_SQL, rows)
        inserted = cur.rowcount
    conn.commit()
    return inserted


if __name__ == "__main__":
    with connect() as conn:
        for url in get_archives():
            month = url[-7:].replace("/", "-")
            games = get_games(url)
            inserted = save_games(conn, games, month)
            print(f"{month}: {len(games)} partidas, {inserted} nuevas")