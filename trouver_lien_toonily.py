#On associe l'anime avec le lien que l'on aura : 
import requests
from bs4 import BeautifulSoup
import sys
import io
from manga import BDDManga
import os

#Bug d'écriture sinon
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def lien_final(url,bdd):
    list_episode = []
    reponse = requests.get(url)
    if reponse.ok:
        soup = BeautifulSoup(reponse.text,"html.parser")
        
        episodes = soup.find_all('li', class_="wp-manga-chapter")
        for episode in episodes :
            list_episode.append(episode.find("a")["href"])

        
    return list_episode


