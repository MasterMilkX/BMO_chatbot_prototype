import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import wget
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.action_chains import ActionChains
import zipfile
import os

def main():
  
    url = "https://www.microstudio.dev/explore/"
    
    driver = webdriver.Chrome('chromedriver.exe') 
    driver.get(url) 
    
    # this is just to ensure that the page is loaded
    time.sleep(5) 

    dropdown = driver.find_element("id","explore-box-list")
    dropdown.click()

    actions = ActionChains(driver)
    for _ in range(500):
        actions.send_keys(Keys.SPACE).perform()
        time.sleep(0.2)
    
    html = driver.page_source
    driver.close() # closing the webdriver

    soup = BeautifulSoup(html, "html.parser")
    all_divs = soup.findAll('img', {'class' : 'poster'})

    # download and extract the code file from the poster url
    print(len(all_divs), "games found")

    links = []
    # store the urls in a csv file
    for i, div in enumerate(all_divs):
        links.append(div.attrs['src'])
    
    # store an array into a csv
    with open('links.txt', 'w') as f:
        for item in links:
            temp = author_game(item)
            temp = "https://microstudio.dev"+temp+"/export/project/"
            f.write(temp + '\n')


    file1 = open('links.txt', 'r')
    lines = file1.readlines()

    for line in lines:
        url = line
        url_name = "_".join(author_game(url).split("/")[1:])
        wget.download(url, url_name + '.zip')
        extract_zip(url_name)
        # os.remove(url_name + '.zip')
  
# extract ms folder from the zip file
def extract_zip(file_name):
    archive = zipfile.ZipFile(file_name+'.zip')

    for file in archive.namelist():
        if file.startswith('ms'):
            archive.extract(file, 'codes/'+file_name)
        if file.startswith('sprites'):
            archive.extract(file, 'sprites/'+file_name)

# find source 
def author_game(string):
    index = []
    for i, c in enumerate(string):
        if c == '/':
            index.append(i)
    return string[index[2] : index[4]]

if __name__ == '__main__':
    main()