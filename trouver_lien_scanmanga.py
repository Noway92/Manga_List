#On associe l'anime avec le lien que l'on aura : 
import requests
from bs4 import BeautifulSoup
import sys
import io
from manga import BDDManga
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re

#Bug d'écriture sinon
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def lien_final(url,bdd):
    list_episode = []
    liste_numéro_chapitre= []
    # Options pour Chrome (comme le mode headless)
    options = webdriver.ChromeOptions()

    options.add_argument('--headless')  # Lance Chrome(sans interface graphique)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36')

    # Initialisation du driver
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    page_source = driver.page_source

    driver.quit()
    #ICI ERREUR
    
    soup = BeautifulSoup(page_source, "html.parser")   
    episodes = soup.find_all('td', class_="publi_read")
    for episode in episodes :
        chaine = episode.find("a")["href"]
        list_episode.append(episode.find("a")["href"])
        match = re.search(r'Chapitre-(.*?)-', chaine)
        if match:
            liste_numéro_chapitre.append(match.group(1).strip())
        else:
            liste_numéro_chapitre.append(None)


        
    return list_episode,liste_numéro_chapitre


