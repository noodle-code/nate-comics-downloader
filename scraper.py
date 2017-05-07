from bs4 import BeautifulSoup
from urllib.parse import urlparse

import os
import re
import requests
import urllib.request

url = ''
chapters = []
base_url = ''
comic_dir = os.getcwd() + '\comic'
current_comic = ''
nextPage = True


def checkDirectory(directory):
    if not os.path.isdir(directory):
        print("Cannot find direcotry: " + directory + ". Creating it instead.")
        os.makedirs(directory)
        print('Folder created')
    return

def checkComicFolder(folder):
    global comic_dir
    global current_comic

    current_comic = comic_dir + "\\" + folder
    checkDirectory(current_comic)

    return

def getbaseurl(url):
    global base_url
    rawurl = urlparse(url)
    base_url = rawurl.scheme + '://' + rawurl.netloc
    return

def isLinkSpecific(url):
    pattern = re.compile(r'detail.php')

    return pattern.search(url)

def parseUrlToObject(url):
    return_data = requests.get(url)
    data = return_data.text
    soupObject = BeautifulSoup(data, 'html.parser')
    return soupObject

def getchapters(soup):
    global chapters

    chapter_list = soup.find('ul', { "class" : "tel_list" })

    for link in chapter_list.find_all('li', { "class" : "first"}):
        for ref in link.find_all('a'):
            chapters.append(ref.get('href'))
    return

def getImage(url):
    global chapters
    global comic_dir
    global current_comic
    ch_title = ''

    # raw = requests.get(url)
    # rawData = raw.text
    # cur_chap = BeautifulSoup(rawData, "html.parser")
    cur_chap = parseUrlToObject(url)

    ch_info = cur_chap.find('div', { "class" : "tvi_episodeInfo" })
    ch_num = ch_info.find('span', { "class" : "tvi_episodeNum" })
    ch_desc = ch_info.find('span', { "class" : "tvi_episodeTitle" })
    ch_title = ch_num.string + ch_desc.string

    print('Downloading ' + ch_title)

    filename = current_comic + "\\" + ch_title + ".jpg"

    if not os.path.isfile(filename):
        img_holder = cur_chap.find('div', { "class" : "toonView" })
        comic_img = img_holder.find('img')
        img_url = comic_img.get('src')

        with open(filename, "wb") as f:
            f.write(requests.get(img_url).content)
    else:
        print("Chapter already exists. Skipping...")

    return

def getNextPage(soup):
    nextPage = False
    paging = soup.find('div', { "class" : "paging" })
    forwardLink = paging.find('a', { "class" : "next" })
    if forwardLink:
        nextPage = forwardLink.get('href')

    return nextPage

def dlImageFromLink(url):
    print("Starting chapter download...")
    getImage(url)
    return

def dlChaptersFromLink(url):
    global nextPage

    print("Scraping for available chapters...")

    while nextPage:

        soup = parseUrlToObject(url)
        getchapters(soup)

        nextPage = getNextPage(soup)

        if nextPage:
            url = base_url + nextPage

    print("Starting download of chapter images...")

    for chapter in reversed(chapters):
        getImage(base_url + chapter)

# Init
checkDirectory(comic_dir)

url = input("Enter URL: ")
getbaseurl(url)

folder = input("Folder name for downloads: ")
checkComicFolder(folder)

if isLinkSpecific(url):
    dlImageFromLink(url)
else:
    dlChaptersFromLink(url)

print('Scraping finished')
