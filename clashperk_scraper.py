from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import os
import time
# PYPPETEER_CHROMIUM_REVISION = '1263111'
# os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION
# # os.environ['PYPPETEER_SKIP_CHROMIUM_DOWNLOAD'] = 'true'

# from pyppeteer import launch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
GOOGLE_CHROME_PATH = '/app/.chrome-for-testing/chrome-linux64/chrome'
CHROMEDRIVER_PATH = '/app/.chrome-for-testing/chromedriver-linux64/chromedriver'

clashperk_war_history_url = "https://clashperk.com/web/players/%s/wars"

async def format_war_stats(stats):
    lines = []

    lines.append(f"**Overall Hitrate:** {stats['OverallHitrate']*100:.1f}%")
    lines.append(f"**Total Attacks:** {stats['TotalHits']}")
    lines.append(f"**3⭐ Rate:** {stats[3]}/{stats['TotalHits']} ({(stats[3]/stats['TotalHits'])*100:.1f}%)\n")

    for war_type in ["CWL", "Normal"]:
        wt_data = stats[war_type]
        lines.append(f"__**{war_type} Wars:**__")
        lines.append(f"> Overall Hitrate: {wt_data['OverallHitrate']*100:.1f}%")
        lines.append(f"> Total Hits: {wt_data['TotalHits']}")
        lines.append(f"> 3⭐ Rate: {wt_data[3]}/{wt_data['TotalHits']} ({(wt_data[3]/wt_data['TotalHits'])*100:.1f}%)\n")

        # Get only TH attacker keys (skip 'OverallHitrate', etc.)
        attacker_townhalls = [k for k in wt_data.keys() if str(k).startswith("TH")]

        for atk_th in attacker_townhalls:
            for def_th, result in wt_data[atk_th].items():
                lines.append(f"**{atk_th} → {def_th}**")
                lines.append(f"> Hits: {result['TotalHits']}")
                lines.append(f"> Avg Stars: {result['Stars']:.2f}")
                lines.append(f"> Avg %: {result['Percentage']:.1f}%")
                lines.append(f"> 3⭐ Rate: {result[3]}/{result['TotalHits']} ({(result[3]/result['TotalHits'])*100:.1f}%)")
                lines.append(f"> Star Breakdown: 0⭐={result[0]}, 1⭐={result[1]}, 2⭐={result[2]}, 3⭐={result[3]}\n")

    return "\n".join(lines)

async def fetch_rendered_html(url):
    
    if os.environ.get("deployed", "development") == "deployment":
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-web-security")
        options.add_argument("--remote-allow-origins=*")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--remote-debugging-address=0.0.0.0")
        options.binary_location = GOOGLE_CHROME_PATH
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-web-security")
        options.add_argument("--remote-allow-origins=*")
        driver = webdriver.Chrome(options=options)
    
    driver.get(url)
    time.sleep(3)
    content = driver.page_source
    driver.quit()
    # browser = await launch(headless=True, args=['--no-sandbox'])
    # page = await browser.newPage()
    # await page.goto(url, {'waitUntil': 'networkidle2', 'timeout':0})
    # content = await page.content()
    # await browser.close()
    return content

async def average_player_war_data(war_data):
    averaged_data = {"CWL":{"OverallHitrate":0, 0:0, 1:0, 2:0, 3:0, "TotalHits":0}, 
                     "Normal":{"OverallHitrate":0, 0:0, 1:0, 2:0, 3:0, "TotalHits":0}, 
                     "OverallHitrate":0, 0:0, 1:0, 2:0, 3:0, "TotalHits":0}
    for war in war_data:
        war_type = war["WarType"]
        attacker_townhall = war["AttackTH"]
        defender_townhall = war["DefendTH"]
        star_count = war["Stars"]
        percentage = war["Percentage"]
        
        if not attacker_townhall in averaged_data[war_type].keys():
            averaged_data[war_type][attacker_townhall] = {}
        if not defender_townhall in averaged_data[war_type][attacker_townhall].keys():
            averaged_data[war_type][attacker_townhall][defender_townhall] = {"Stars":0, "Percentage":0, "OverallHitrate":0, 0:0, 1:0, 2:0, 3:0, "TotalHits":0}
        averaged_data[star_count] += 1
        averaged_data[war_type][star_count] += 1
        averaged_data[war_type][attacker_townhall][defender_townhall][star_count] += 1
        averaged_data["TotalHits"] += 1
        averaged_data[war_type]["TotalHits"] += 1
        averaged_data[war_type][attacker_townhall][defender_townhall]["TotalHits"] += 1
        if star_count == 3:
            averaged_data["OverallHitrate"] += 1
            averaged_data[war_type]["OverallHitrate"] += 1
            averaged_data[war_type][attacker_townhall][defender_townhall]["OverallHitrate"] += 1
        averaged_data[war_type][attacker_townhall][defender_townhall]["Stars"] += star_count
        averaged_data[war_type][attacker_townhall][defender_townhall]["Percentage"] += percentage
    averaged_data["OverallHitrate"] /= averaged_data["TotalHits"]
    averaged_data["CWL"]["OverallHitrate"] /= averaged_data["CWL"]["TotalHits"]
    averaged_data["Normal"]["OverallHitrate"] /= averaged_data["Normal"]["TotalHits"]
    for war_type in ["CWL", "Normal"]:
        for attacker_townhall in list(averaged_data[war_type].keys())[6:]:
            for defender_townhall in averaged_data[war_type][attacker_townhall].keys():
                averaged_data[war_type][attacker_townhall][defender_townhall]["OverallHitrate"] /= averaged_data[war_type][attacker_townhall][defender_townhall]["TotalHits"]
                averaged_data[war_type][attacker_townhall][defender_townhall]["Stars"] /= averaged_data[war_type][attacker_townhall][defender_townhall]["TotalHits"]
                averaged_data[war_type][attacker_townhall][defender_townhall]["Percentage"] /= averaged_data[war_type][attacker_townhall][defender_townhall]["TotalHits"]
    return averaged_data

async def get_player_war_data(player_tag):
    url = clashperk_war_history_url % player_tag.replace("#", "%23")
    html = await fetch_rendered_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    history = soup.find('tbody', class_="MuiTableBody-root mui-y6j1my").find_all('tr', class_="MuiTableRow-root mui-wcx5if")
    war_attacks = []
    for row in history:
        attacker_townhall = row.find('p', class_="MuiTypography-root MuiTypography-body2 mui-182umzi").text
        stars = row.find_all('div', class_="MuiStack-root mui-1xhj18k")
        percentages = row.find_all('p', class_="MuiTypography-root MuiTypography-body2 mui-175els0")
        defender_townhalls = row.find_all('p', class_="MuiTypography-root MuiTypography-body2 mui-zd1gib")
        war_type = "CWL" if len(row.find('span', style="color: rgb(29, 161, 242); font-weight: 600;")) > 0 else "Normal"       
        match_up = row.find('p', class_="MuiTypography-root MuiTypography-body2 mui-14exzr2").text
        attack_count = 1
        for attack in range(len(row.find_all('div', class_="MuiStack-root mui-1xhj18k"))):
            star_count = len(stars[attack].find_all('svg', class_="MuiSvgIcon-root MuiSvgIcon-fontSizeMedium mui-1vw3m0b")) + len(stars[attack].find_all('svg', class_="MuiSvgIcon-root MuiSvgIcon-fontSizeMedium mui-qtph5r"))
            percentage = percentages[attack].text[:-1]
            defender_townhall = defender_townhalls[attack].text
            war_attacks.append({"AttackTH":"TH" + attacker_townhall, "Stars":star_count, "Percentage":int(percentage), "DefendTH":"TH" + defender_townhall, "WarType":war_type, "MatchUp":match_up})
            attack_count += 1
    # print(war_attacks)
    # print(average_player_war_data(war_attacks))
    print(f"War data collected for tag:{player_tag}")
    average_war_data = await average_player_war_data(war_attacks)
    print(f"Averaged data for tag:{player_tag}")
    formatted_data = await format_war_stats(average_war_data)
    print(f"Formatted data for tag:{player_tag}")
    return formatted_data

result = get_player_war_data("#YG8082JP")
print(result)
