"""
Author: Ashna Jain
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

#url = 'http://www.codaspy.org/2022/accepted.html'
#url = 'http://www.codaspy.org/2022/accepted-posters.html'
url = 'https://cvpr2022.thecvf.com/tutorial-selections'

def getDataIEEE(url):
    #load the webpage content
    html_text = requests.get(url).text
    #convert to a BeautifulSoup object
    soup = BeautifulSoup(html_text, 'lxml')
    contents = soup.find_all('td')
    if(contents == None):
        return "provide another URL"
    paper_titles = []
    author_names = []
    df = pd.DataFrame(columns=('Paper Title', 'Authors'), index=np.arange(0, len(contents)))

    for i in range(len(contents)):
        if(i % 2 == 0):
            paper_titles.append(contents[i].text)
        else:
            author_names.append(contents[i].text)
        i = i+1
    for i in range(len(paper_titles)):
        df.loc[i] = [paper_titles[i], author_names[i]]
    print(df)
    return df

def getDataAMC(url):
    #load the webpage content
    html_text = requests.get(url).text
    #convert to a BeautifulSoup object
    soup = BeautifulSoup(html_text, 'lxml')
    contents = soup.find_all('tr')
    if(contents == None):
        return "provide another URL"
    paper_titles = []
    author_names = []
    df = pd.DataFrame(columns=('Paper Title', 'Authors'), index=np.arange(0, len(contents)))

    for c in contents:
        paper_titles.append(c.find('td').text)
        author_names.append(c.find('td').find_next_sibling().text)
    for i in range(len(paper_titles)):
        df.loc[i] = [paper_titles[i], author_names[i]]
    print(df)
    return df

#getPaperPosterData(url)
getData(url)
