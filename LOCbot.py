import discord
import discord.ext.commands
from database_manager import commit_close, commit_close_with_parameters, get_user_by_discord_id, check_user_by_player_tag
import requests
import json
from bot_errors import CurlResponseError403, DuplicateTagError, NoPlayerTagsError, ClaimedTagError
from bot import Bot
import discord.ext
import os

if os.environ.get("deployed", "development") == "deployment":
    API_TOKEN = os.environ.get("discord_key")
    clash_api_token = os.environ.get("clash_key")
    os.environ['http_proxy'] = os.getenv('NSCRIPTIOD_HTTP')
    os.environ['https_proxy'] = os.getenv('NSCRIPTIOD_HTTP')
    r = requests.get('https://ipinfo.io/ip')
    remoteIp=r.text
    print('IP: '+remoteIp)
else:
    API_TOKEN = open('apikeydiscord.txt', 'r').read()
    clash_api_token = open('apikeyclash.txt', 'r').read()

from clashperk_scraper import get_player_war_data

headers = {
    "Authorization": f"Bearer {clash_api_token}"
}
clash_api_url = "https://api.clashofclans.com/v1/players/%s"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = Bot(command_prefix="!", intents=intents)

@bot.command()
async def setup(ctx, *, arg):
    print(f"!setup command from {ctx.author}")
    if arg.startswith("player_tag:"):
        try:
            tag = arg.split(":", 1)[1].strip().strip("'\"")
            response = requests.get(clash_api_url % tag.replace("#", "%23"), headers=headers)
            print(f"COC API status code: {response.status_code}")
            if response.status_code == 403:
                raise CurlResponseError403
            elif response.status_code != 200:
                raise IndexError
            discord_id = ctx.author.id
            tags = json.loads(get_user_by_discord_id(discord_id)[1])
            if tag in tags:
                raise DuplicateTagError
            if check_user_by_player_tag(tag):
                raise ClaimedTagError
            tags.append(tag)
            commit_close_with_parameters("""
                UPDATE users
                SET player_tag = ?
                WHERE discord_id = ?
                """, (json.dumps(tags), discord_id))
            print(tags)
            await ctx.send(f"✅ Received player tag: `{tag}`")
        except IndexError:
            await ctx.send("⚠️ Invalid format or tag does not exist. Use: `!setup player_tag: #YG8082JP`")
        except CurlResponseError403:
            await ctx.send("⚠️ Internal API key or server IP issue")
            print(response.content)
        except DuplicateTagError:
            await ctx.send("⚠️ Tag already registered to you")
        except ClaimedTagError:
            await ctx.send("⚠️ Tag already registered to another user")
    else:
        await ctx.send("⚠️ Expected format: `!setup player_tag: #YG8082JP`")
    
@bot.command()
async def war_stats(ctx, *, arg):
    print(f"!war_stats command from {ctx.author}, command:{arg}")
    if arg.startswith("user:"):
        try:
            discord_id = arg.split(":", 1)[1].strip().strip("'\"")[2:-1]
            member = await bot.fetch_user(discord_id)
            tags = json.loads(get_user_by_discord_id(discord_id)[1])
            if len(tags) == 0:
                raise NoPlayerTagsError
            for tag in tags:
                data = await get_player_war_data(tag)
                await ctx.send(f"Recent War data for tag:{tag}\n" + data)
        except discord.ext.commands.errors.CommandInvokeError:
            await ctx.send(f"⚠️ Invalid Discord ID")
        except IndexError:
            await ctx.send(f"⚠️ Invalid format. Use: `!war_stats user: <@{ctx.author.id}>`")
        except NoPlayerTagsError:
            await ctx.send(f"⚠️ {member.name} has no registered player tags")
    elif arg.startswith("player_tag:"):
        try:
            tag = arg.split(":", 1)[1].strip().strip("'\"")
            print(f"Compiling data for tag:{tag}")
            # response = requests.get(clash_api_url % tag.replace("#", "%23"), headers=headers)
            # print(f"COC API status code: {response.status_code}")
            # if response.status_code == 403:
            #     raise CurlResponseError403
            # elif response.status_code != 200:
            #     raise IndexError
            data = await get_player_war_data(tag)
            await ctx.send(f"Recent War data for tag:{tag}\n" + data)
        except IndexError:
            await ctx.send("⚠️ Invalid format or tag does not exist. Use: `!setup player_tag: #YG8082JP`")
        except CurlResponseError403:
            await ctx.send("⚠️ Internal API key or server IP issue")
            print(response.content)

try:
    bot.run(API_TOKEN)
except KeyboardInterrupt:
    bot.close()