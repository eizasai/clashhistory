import sqlite3
import json

def commit_close(command):
    database = sqlite3.connect("bot.db")
    cursor = database.cursor()
    cursor.execute(command)
    database.commit()
    database.close()

def commit_close_with_parameters(command, parameters):
    database = sqlite3.connect("bot.db")
    cursor = database.cursor()
    cursor.execute(command, parameters)
    database.commit()
    database.close()

def get_user_by_discord_id(discord_id):
    database = sqlite3.connect("bot.db")
    cursor = database.cursor()
    cursor.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
    row = cursor.fetchone()
    if row == None:
        commit_close_with_parameters(f"""
            INSERT INTO users (discord_id, player_tag)
            VALUES(?, ?)
            """, (discord_id, json.dumps([])))
        print(f"Registered {discord_id}")
        cursor.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
    database.close()
    return row

def check_user_by_player_tag(player_tag):
    database = sqlite3.connect("bot.db")
    cursor = database.cursor()
    cursor.execute("SELECT * FROM player_tags WHERE player_tag = ?", (player_tag,))
    row = cursor.fetchone()
    return row != None

commit_close("""
CREATE TABLE IF NOT EXISTS users (
    discord_id TEXT PRIMARY KEY,
    player_tag TEXT
)
""")

commit_close("""
CREATE TABLE IF NOT EXISTS player_tags (
    player_tag TEXT PRIMARY KEY,
    discord_id TEXT    
)
""")