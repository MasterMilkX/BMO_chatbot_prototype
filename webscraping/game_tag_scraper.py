# scrapes from the website: https://steamdb.info/
# gets the tags and description from each game to use for the game data and cross reference features later

import requests
import time
import json
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
from tqdm import tqdm
from nltk.tokenize import word_tokenize
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

driver = None;

###############    HELPER FUNCTIONS   ###############

#retrieve the body content from a link
def getLinkSoup(link,wait_time=1):
    global driver
    if driver is None:
        driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get(link)
    time.sleep(wait_time) #if you want to wait 1 seconds for the page to load
    response = driver.page_source
    soup = BeautifulSoup(response, 'html.parser')
    return soup

#retrieve the body content from a link without using selenium
def quickLinkSoup(link):
    response = requests.get(
        url=link,
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    )
    if response.status_code != 200:
        print(f"> ERROR: Link [{link}] not found... (Response: {response.status_code})")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


###############    SCRAPING   ###############

#retrieve each tag and get their associated links
def getTagLinks():
    #get the list of tags
    tag_list = {}
    tag_soup = getLinkSoup("https://steamdb.info/tags/")
    tag_links = tag_soup.find_all("a",{"class":"label-link"},href=True)
    for tag in tag_links:
        tag_list[tag.text] = tag["href"]
    return tag_list

#retrieve the game names from each tag
def getTagGames(tag_link,max_wait=30):

    #change the select to show all of the games 
    global driver
    if driver is None:
        driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(tag_link)
    select = Select(driver.find_element(by=By.NAME, value='table-apps_length'))  #assume the driver is on the same page still
    select.select_by_value('-1')

    print("> Got the select tag!")

    #wait for some time while it loads
    time.sleep(max_wait)

    #get the list of games
    response = driver.page_source
    soup = BeautifulSoup(response, 'html.parser')
    print("> Got the soup!")

    #grab the name from the table cell text
    game_td = soup.find_all("td",{"class":"text-left"})
    game_names = []
    for td in game_td:
        a = td.find("a",href=True)
        if a is not None:
            game_names.append(a.text)

    print(f"> Got the game names ({len(game_names)} games)!")

    return game_names


###############    MAIN   ###############

DOMAIN = "https://steamdb.info"
LAST_TAG = 0

def main():
    tag_list_links = getTagLinks()
    print(f"> Got the tag list ({len(tag_list_links)} tags)!")

    #get the games for each tag
    tag_games = {}
    i = 0;
    for tag,link in tag_list_links.items():
        i+=1
        if i < LAST_TAG:
            continue

        print(f"-------------------    {tag.upper()}  [{i}/{len(tag_list_links)}]  -------------------")
        tag_games[tag] = getTagGames(DOMAIN+link,20)
        
        
        #export data to a file
        with open("data/tag_games.json","a+") as f:
            f.write(f"{tag}\n")
            f.write("|".join(tag_games[tag]))
            f.write("\n\n")


if __name__ == "__main__":
    main()
