#scrapes from the website: https://gamesdb.launchbox-app.com
# takes game descriptions for parsing later
# use the game descriptions to extract mechanics and features and sort by the genre to suggest to the user later

import requests
import time
import re
import string
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
from tqdm import tqdm
from nltk.tokenize import word_tokenize
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


driver = webdriver.Chrome(ChromeDriverManager().install())

###############    HELPER FUNCTIONS   ###############

#retrieve the body content from a link
def getLinkSoup(link,wait_time=1):
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

#export the data to a file to be read later
def exportData(file,dat):
    with open(file, "w+") as f:
        f.write(dat)

#add more data to the already existing file
def addFileData(file,dat):
    with open(file, "a+") as f:
        f.write(dat)

#





###############    MAIN   ###############

# main function to run the scraping
MAIN_LINK = "https://gamesdb.launchbox-app.com/genres"
DOMAIN = "https://gamesdb.launchbox-app.com"

def main():
    print(DOMAIN)

    #get the genre links first
    gamer_soup = getLinkSoup(MAIN_LINK)
    genre_links_a = gamer_soup.find_all("a",{"class": "list-item"})
    genre_links = [a['href'] for a in genre_links_a]
    print("----  GENRE  ----")
    print(genre_links)

    #get all of the pages on the genre 
    test_genre = genre_links[0]
    print(urljoin(DOMAIN,test_genre))
    genre_soup = getLinkSoup(urljoin(DOMAIN,test_genre))
    last_page_raw = genre_soup.find_all("div",{"class": "pagination-wrapper"})[0].find_all("li",{"class": "last"})[0].find_all("a")[0].text
    last_page = int(re.search("Last \((\d+)\)",last_page_raw).groups()[0])
    pages = [urljoin(DOMAIN,test_genre)+"%7C"+str(i) for i in range(1,last_page+1)]


    print("----  PAGES  ----")
    print(pages)


    #save all the page links to iterate through the game lists
    # game_links_a = genre_soup.find_all("a",{"class": "list-item"})
    # game_links = [a['href'] for a in game_links_a]
    # print("----  GAMES  ----")
    # print(game_links)

    #save all of the game links to iterate through the game descriptions

    #save all of the game descriptions to parse later




if __name__ == "__main__":
    main()