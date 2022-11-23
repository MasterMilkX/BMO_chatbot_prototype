# scrapes from the website: https://gamesdb.launchbox-app.com
# forgot to do on the first run through lol

# import the libraries
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

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

# cleans up the text
def cleanTxt(t):
    return re.sub(r'[^\x00-\x7F]+',' ', t).replace("\r","").replace("\t","").replace("\n","")

#exports the current data to a file
def export2File(data):
    with open("data/tag_games2.txt","w+") as f:
        for t in data:
            f.write(f"{t}\n")
            f.write("|".join(data[t]))
            f.write("\n\n")

#import the data back from the file
def import2File():
    data = {}
    with open("data/tag_games2.txt","r") as f:
        lines = f.readlines()
        i = 0
        while(i < len(lines)):
            if lines[i].strip() == "":
                i += 1
                continue
            else:
                data[lines[i].strip()] = lines[i+1].strip().split("|")
                i += 2
    return data

# main function
EXPORT_CT = 1000  #checkpoints to export the data
LAST_CT = 0      #checkpoints to start again 
if __name__ == "__main__":
    URLS = []
    with open("data/game_urls.txt","r") as f:
        URLS = [l.strip() for l in f.readlines()]

    

    #extract from the tag div
    TAGS = {}
    game_names = []

    #import back in if data already saved
    if(LAST_CT > 0):
        TAGS = import2File()
        game_names = []
        for t in TAGS:
            game_names += TAGS[t]

    #loop through the links
    with tqdm(total=len(URLS[LAST_CT:])) as pbar:
        for ui in range(len(URLS[LAST_CT:])):
            url = URLS[ui]
            #get the html data
            soup = quickLinkSoup(url)
            if soup == None:
                pbar.update(1)
                continue

            #grab the tags of the game
            headers = soup.find_all("td",{"class":"row-header"})

            #get the name of the game
            name_head = [h for h in headers if h.text == "Name"][0]
            name = name_head.find_next_sibling("td").findChildren("span",{"class":"view"})[0].text
            name = cleanTxt(name)

            #check if already saved
            if name in game_names:
                pbar.update(1)
                continue
            else:
                game_names.append(name)

            #get the tags
            tag_head = [h for h in headers if h.text == "Genres"][0]
            # print(tag_head.find_next_sibling("td").find())
            tags = tag_head.find_next_sibling("td").findChildren("span",{"class":"view"})[0].text
            

            #break up the tags and add the game name
            tags = tags.split(",")
            tags = [cleanTxt(t).strip() for t in tags]
            for t in tags:
                if t not in TAGS:
                    TAGS[t] = [name]
                else:
                    TAGS[t].append(name)

            

            #export the tags intermittently   
            if (ui % EXPORT_CT == 0) and (ui != 0):
                print(f"Exporting... ( LAST SET {ui+LAST_CT} )")
                export2File(TAGS)

            pbar.update(1)
            pbar.set_description(f"Last game: {name}")

    #export the tags one last time
    export2File(TAGS)
    

