# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # remove this if you want to see the browser
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

PYPPETEER_CHROMIUM_REVISION = '1263111'
import os
os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION
from requests_html import HTMLSession

session = HTMLSession()

clashperk_war_history_url = "https://clashperk.com/web/players/%s/wars"


def get_player_war_data(player_tag):
    # driver.get(clashperk_war_history_url % player_tag.replace("#", "%23"))
    # try:
    #     WebDriverWait(driver, 15).until(
    #         EC.presence_of_element_located((By.CSS_SELECTOR, ".war-row"))  # example class
    #     )
    #     print("Page loaded!")
    # except:
    #     print("Timeout waiting for page to load.")
    # soup = BeautifulSoup(driver.page_source, 'html.parser')

    r = session.get(clashperk_war_history_url % player_tag.replace("#", "%23"))
    r.html.render(sleep=15, timeout=30)
    soup = BeautifulSoup(r.html.html, 'html.parser')

    history = soup.find('tbody', class_="MuiTableBody-root mui-y6j1my").find_all('tr', class_="MuiTableRow-root mui-wcx5if")
    war_attacks = []
    for row in history:
        attacker_townhall = row.find('p', class_="MuiTypography-root MuiTypography-body2 mui-182umzi").text
        stars = row.find_all('div', class_="MuiStack-root mui-1xhj18k")
        percentages = row.find_all('p', class_="MuiTypography-root MuiTypography-body2 mui-175els0")
        defender_townhalls = row.find_all('p', class_="MuiTypography-root MuiTypography-body2 mui-zd1gib")
        attack_count = 1
        for attack in range(len(row.find_all('div', class_="MuiStack-root mui-1xhj18k"))):
            star_count = len(stars[attack].find_all('svg', class_="MuiSvgIcon-root MuiSvgIcon-fontSizeMedium mui-1vw3m0b")) + len(stars[attack].find_all('svg', class_="MuiSvgIcon-root MuiSvgIcon-fontSizeMedium mui-qtph5r"))
            percentage = percentages[attack].text[:-1]
            defender_townhall = defender_townhalls[attack].text
            war_attacks.append({"AttackTH":attacker_townhall, "Stars":star_count, "Percentage":percentage, "DefendTH":defender_townhall})
            attack_count += 1
    print(war_attacks)

# get_player_war_data("#YG8082JP")
