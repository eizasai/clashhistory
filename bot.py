import discord
import json
import sqlite3
import json
from database_manager import commit_close, commit_close_with_parameters, get_user_by_discord_id
from discord.ext import commands
import os

if os.getlogin == "eizak":
    clash_api_token = open('apikeyclash.txt', 'r').read()
else:
    clash_api_token = os.environ.get("clash_key")
    
headers = {
    "Authorization": f"Bearer {clash_api_token}"
}
clash_api_url = "https://api.clashofclans.com/v1/players/%s"
clashperk_war_history_url = "https://clashperk.com/web/players/%s/wars"

class Bot(commands.Bot):
    server_rules_channel = 1370566880934367392
    our_clans_channel = 1370565218794733568
    apply_channel = 1370560686916370484
    server_test_channel = 1370564001754386503
    async def on_ready(self):
        print(f'logged on as {self.user}')
    async def on_member_join(self, member):
        print(f"{member} joined the server.")
        try:
            commit_close_with_parameters(f"""
                INSERT INTO users (discord_id, player_tag)
                VALUES(?, ?)
                """, (member.id, json.dumps([])))
            print(f"Registered {member}")
            await member.send(
                f"👋 Welcome to **{member.guild.name}**, {member.name}!\n"
                "To get started, use !setup tag:'tag' api_token:'api_token' to link accounts"
            )
            await member.send("You should be set up now\n" +
                "Check out these channels!\n" +
                f"<#{self.server_rules_channel}>\n" + 
                f"<#{self.our_clans_channel}>\n" + 
                f"<#{self.apply_channel}>")
        except discord.Forbidden:
            print("Couldn't send DM to the new member.")
        except sqlite3.IntegrityError:
            print(f"{member} Discord already registered")
            await member.send(
                f"👋 Welcome back to **{member.guild.name}**, {member.name}!\n"
                "use !setup tag:'tag' api_token:'api_token' to link accounts"
            )
            await member.send("You should be set up now\n" +
                "Check out these channels!\n" +
                f"<#{self.server_rules_channel}>\n" + 
                f"<#{self.our_clans_channel}>\n" + 
                f"<#{self.apply_channel}>")
