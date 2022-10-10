#scrapes from the website: https://gamesdb.launchbox-app.com/genres
# takes game descriptions for parsing later
# use the game descriptions to extract mechanics and features and sort by the genre to suggest to the user later

import requests
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
import re
from tqdm import tqdm
from nltk.tokenize import word_tokenize
import string



###############    HELPER FUNCTIONS   ###############

#retrieve the body content from a link
def getLinkSoup(link):
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

#





###############    MAIN   ###############

# main function to run the scraping
TEST_LINK = "https://gamesdb.launchbox-app.com/genres"

def main():
    #get the genre links first
    gamer_soup = getLinkSoup(TEST_LINK)
    genre_links_a = gamer_soup.find_all("a",{"class": "list-item"})
    genre_links = [a['href'] for a in genre_links_a]
    print(genre_links)

    #save all the genre links to iterate through the game lists

    #save all of the game links to iterate through the game descriptions

    #save all of the game descriptions to parse later

    


if __name__ == "__main__":
    main()