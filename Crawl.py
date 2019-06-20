import time
import urllib

import bs4
import requests
import re
import argparse


import warnings
warnings.filterwarnings("ignore")

def get_first_link(url):
    #open the page
    page = requests.get(url)
    #parse html using BeautifulSoup
    soup = bs4.BeautifulSoup(page.text)
    #find main content of the page
    content = soup.find(id='mw-content-text')
    
    #get rid of all italic/footnote/table sections of the page
    for s in content.find_all(["i", "sup", "table"]):
        s.replace_with("")
    #get rid of links wih red flag (non-existing articles, that has redlink=1 as parameter)
    for s in content.find_all(["a"]):
        if "redlink=1" in s:
            s.replace_with("")
    #get rid of images, as they're identified as links and we don't want them
    for s in content.find_all(class_ = 'image'):
        s.replace_with("")
        
    #to remove parentheses and boxes i choose to remove them with regex
    content = str(content)
    #remove parentheses
    content = re.sub(r' \(.*?\)', '', content)
    #remove squares
    content = re.sub(r' \[.*?\]', '', content)
    
    #now use BeautifulSoup again to find first link in the page that link to another wiki
    co = bs4.BeautifulSoup(content)
    fr = co.find(href = re.compile('/wiki/'))
    return fr


#take a wikipedia link as an argument (optional)
ap = argparse.ArgumentParser()
ap.add_argument("-u", "--url", help="url of wikipedia to start with", default='https://en.wikipedia.org/wiki/Special:Random')
args = vars(ap.parse_args())

#start from this link
last_url = args["url"]
#our phi link
phi_url = "https://en.wikipedia.org/wiki/Philosophy"

#mark the pages we already visited, to check if we're stuck in a loop.
visited = set()

while True:
    #first open page using requests before printing, to not print Random page
    last_url = requests.get(last_url)
    last_url = last_url.url
    print(last_url)

    if last_url == phi_url:
        print("We've reached the Philosophy page.")
        break
    elif last_url in visited:
        print("Stuck in a loop.")
        break

    visited.add(last_url)

    first_link = get_first_link(last_url)
    if not first_link:
        print("A page with no outgoing links.")
        break
        
    #new page link
    last_url = 'http://en.wikipedia.org' + first_link.get('href')
    
    #avoid heavy load on wikipedia
    time.sleep(5) 

