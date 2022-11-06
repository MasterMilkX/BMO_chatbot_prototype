#scrapes from the website: https://gamesdb.launchbox-app.com
# takes game descriptions for parsing later
# use the game descriptions to extract mechanics and features and sort by the genre to suggest to the user later

# Also look at https://steamdb.info/ for more data

import requests
import time
import re
import os
import string
import sys
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
from tqdm import tqdm
from nltk.tokenize import word_tokenize
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

driver = None;

###############    HELPER FUNCTIONS   ###############

#retrieve the body content from a link
def getLinkSoup(link,wait_time=1):
    global driver
    if driver is None:
        driver = webdriver.Chrome(ChromeDriverManager().install())

    # response = requests.get(
    #     url=link,
    #     headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    # )
    # if response.status_code != 200:
    #     print(f"> ERROR: Link [{link}] not found... (Response: {response.status_code})")
    #     return None
    # soup = BeautifulSoup(response.content, 'html.parser')
    # return soup
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


#export the data to a file to be read later
def exportData(file,dat):
    with open(file, "w+") as f:
        f.write(dat)

#add more data to the already existing file
def addFileData(file,dat):
    with open(file, "a+") as f:
        f.write(dat)





###############    MAIN   ###############

# main function to run the scraping
MAIN_LINK = "https://gamesdb.launchbox-app.com/genres"
DOMAIN = "https://gamesdb.launchbox-app.com"
GAME_PAGE_FILE = "data/game_data.txt";
GAME_DESC_FILE = "data/game_desc.txt";

def saveGameLinks(genre_num=0,page_num=0):
    print(DOMAIN)
    game_index = (sum(1 for _ in open(GAME_PAGE_FILE)) if os.path.isfile(GAME_PAGE_FILE) else 0)

    #get the genre links first
    gamer_soup = getLinkSoup(MAIN_LINK)
    genre_links_a = gamer_soup.find_all("a",{"class": "list-item"})
    genre_links = [a['href'] for a in genre_links_a]
    # print(genre_links)

    #get all of the pages on the genre 
    for genre in genre_links[genre_num:]:
        print(f"======   GENRE: {genre}    ======")
        genre_soup = getLinkSoup(urljoin(DOMAIN,genre),0.25)
        last_page_raw = genre_soup.find_all("div",{"class": "pagination-wrapper"})[0].find_all("li",{"class": "last"})[0].find_all("a")[0].text
        last_page = int(re.search("Last \((\d+)\)",last_page_raw).groups()[0])
        pages = [urljoin(DOMAIN,genre)+"%7C"+str(i) for i in range(1,last_page+1)]

        #save all the game links
        for pi in range(len(pages))[page_num:]:
            p = pages[pi]
            print(f"---- PAGE # [{pi+1}/{len(pages)}] ({game_index} GAMES SAVED)  ----")
            page_soup = getLinkSoup(p,0.1)
            game_links_a = page_soup.find_all("a",{"class": "list-item"})
            game_links = [a['href'] for a in game_links_a]
            game_links_full = [urljoin(DOMAIN,gl) for gl in game_links]

            #write the list to a file
            with open(GAME_PAGE_FILE, "a+") as f:
                for g in game_links_full:
                    f.write(g+"\n")

            game_index += len(game_links_full)

# cleans up the text
def cleanTxt(t):
    return re.sub(r'[^\x00-\x7F]+',' ', t).replace("\r","").replace("\t","").replace("\n","")

# get each game's description from their link
def saveGameDescriptions(game_index=0):
    
    game_links = []
    with open(GAME_PAGE_FILE, "r") as f:
        game_links = f.read().splitlines()

    # go through each link and extract the name and description
    game_names = []
    for g in game_links[game_index:]:
        game_index += 1

        #get the game description
        soup = quickLinkSoup(g)

        #grab the title of the game
        headers = soup.find_all("td",{"class":"row-header"})
        name_head = [h for h in headers if h.text == "Name"][0]
        name = name_head.find_next_sibling("td").findChildren("span",{"class":"view"})[0].text
        name = cleanTxt(name)

        if name in game_names:
            print(f"DUPLICATE GAME: {name}")
            continue
        else:
            game_names.append(name)

        #grab the description of the game
        desc_head = [h for h in headers if h.text == "Overview"][0]
        desc = desc_head.find_next_sibling("td").findChildren("div",{"class":"view"})[0].text
        desc = cleanTxt(desc)

        #print to a file
        with open(GAME_DESC_FILE, "a+") as f:
            f.write(f"{name}\n{desc}\n\n")

        # print(g)
        # print(name)
        # print(desc)
        # print("")

        print(f"---- GAME # [{game_index}/{len(game_links)}] | {name} ----")




#just for testing soup commands and output
def soupTest(link):
    soup = quickLinkSoup(link)

    #grab the title of the game
    headers = soup.find_all("td",{"class":"row-header"})
    name_head = [h for h in headers if h.text == "Name"][0]
    name = name_head.find_next_sibling("td").findChildren("span",{"class":"view"})[0].text

    #grab the description of the game
    desc_head = [h for h in headers if h.text == "Overview"][0]
    desc = desc_head.find_next_sibling("td").findChildren("div",{"class":"view"})[0].text

    print(name)
    print(desc)



if __name__ == "__main__":
    # saveGameLinks()
    # soupTest("https://gamesdb.launchbox-app.com/games/details/79189")
    saveGameDescriptions(0 if len(sys.argv) < 2 else int(sys.argv[1]))