import requests
from bs4 import BeautifulSoup
import os
import json

if os.environ.get("deployed", "development") == "deployment":
    clash_api_token = os.environ.get("clash_key")
else:
    clash_api_token = open('apikeyclash.txt', 'r').read()

headers = {
    "Authorization": f"Bearer {clash_api_token}"
}

clash_of_stats_player_url = "https://www.clashofstats.com/players/%s/summary"
clash_api_war_log_url = "https://api.clashofclans.com/v1/clans/%s/warlog?limit=1"

def get_player_clan_history(player_tag):
    player_url = clash_of_stats_player_url % player_tag.replace("#", "")
    response = requests.get(player_url)
    
    soup = BeautifulSoup(response.content, 'html.parser')

    clans = soup.find_all('span', class_='text--secondary caption')
    clan_tags = []
    for clan in clans:
        clan_tags.append(clan.text.replace("-", "").strip())
    return clan_tags


def get_war_log_history(clan_tag):
    clan_war_log_url = clash_api_war_log_url % clan_tag.replace("#", "%23")
    response = requests.get(clan_war_log_url, headers=headers)
    war_log_data = json.loads(response.content)
    print(war_log_data)

def get_player_war_history(player_tag):
    clan_war_tags = get_player_clan_history(player_tag)
    for clan_war_tag in clan_war_tags[0:1]:
        get_war_log_history(clan_war_tag)

get_player_war_history("#Y0R0R2QQJ")