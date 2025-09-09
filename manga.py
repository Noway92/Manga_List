import requests
from bs4 import BeautifulSoup
import sys
import io
import csv
import pandas as pd
import numpy as np
import re # C'est pour récup la page
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta


#Bug d'écriture sinon
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class BDDManga:
    def __init__(self):
        self.list_nom=[]
        self.list_dernier_vu=[]

        self.list_toonily_nom = []      
        self.list_toonily_lien =[]

        self.list_MangaDemon_lien = []
        self.list_MangaDemon_nom = []

        self.list_ScanManga_lien = []
        self.list_ScanManga_nom=[]

        
    @property
    def List_Nom(self):
        return self.list_nom
    @property
    def List_Dernier_Vu(self):
        return  self.list_dernier_vu    
    
    
    @property
    def List_Toonily_Lien(self):
        return  self.list_toonily_lien
    @property
    def List_Toonily_Nom(self):
        return  self.list_toonily_nom
       
    
    @property
    def List_MangaDemon_Lien(self):
        return self.list_MangaDemon_lien
    @property
    def List_MangaDemon_Nom(self):
        return self.list_MangaDemon_nom
    
     
    
    @property
    def List_ScanManga_Lien(self):
        return self.list_ScanManga_lien
    @property
    def List_ScanManga_Nom(self):
        return self.list_ScanManga_nom
    
    

    
    def creer_bdd_toonily(self): 
        
        # Ici on fait la première boucle pour récupérer la page 1 
        url = "https://toonily.com/webtoons/?m_orderby=alphabet"
        reponse = requests.get(url)
        if reponse.ok:
            soup = BeautifulSoup(reponse.text,"html.parser")
            
            animes = soup.find_all('div', class_="col-6 col-sm-3 col-lg-2 badge-pos-2")
            for anime in animes :
                a = anime.find('a')
                self.list_toonily_nom.append(a["title"].lower())
                self.list_toonily_lien.append(a["href"])

            # Cherchons le nombre de pages
            inter = re.search(r'/page/(\d+)/', soup.find('a', class_="last")["href"])
            lastpage=inter.group(1)


        
        #for i in range(2,5):
        for i in range(2,int(lastpage)+1):
            url2 = "https://toonily.com/webtoons/page/"+str(i)+"/?m_orderby=alphabet"
            reponse = requests.get(url2)
            if reponse.ok:
                soup = BeautifulSoup(reponse.text,"html.parser")                
                animes2 = soup.find_all('div', class_="col-6 col-sm-3 col-lg-2 badge-pos-2")
                for anime in animes2 :
                    a = anime.find('a')
                    self.list_toonily_nom.append(a["title"].lower())
                    self.list_toonily_lien.append(a["href"])

    def creer_bdd_MangaDemon(self):

        i=1
        #for i in range(2,5):
        test=True
        while(test):
            url2 = "https://mgdemon.org/browse.php?list="+str(i)
            reponse = requests.get(url2)
            if reponse.ok:
                soup = BeautifulSoup(reponse.text,"html.parser")
                div = soup.find('div',id="content")
                animes = div.find_all('li')
                #Condition pour arréter
                if(len(animes)==0):                    
                    test=False
                else:                    
                    for anime in animes :
                        a = anime.find('a')
                        self.list_MangaDemon_nom.append(a["title"].lower())
                        self.list_MangaDemon_lien.append("https://mgdemon.org"+a["href"])
                
            i=i+1
        
    def creer_bdd_ScanManga(self):
        #Utiliser selenium car ici le request est bloqué
        

        url = "https://www.scan-manga.com/scanlation/liste_series.html"
        # Options pour Chrome (comme le mode headless)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Lance Chrome en mode headless (sans interface graphique)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36')

        # Initialisation du driver
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        page_source = driver.page_source

        driver.quit()
        soup = BeautifulSoup(page_source, "html.parser")
        
        #print(soup.prettify()) Pour voir le contenu de soup        

        #On veut tout ce qui comment par listing et finit par listing
        pattern = re.compile(r'^listing.*listing$')    
        animes = soup.find_all('div', class_=pattern)
        for anime in animes :
            a = anime.find('a')
            if(a is not None):
                #Strip c'est pour enlever les espaces
                self.list_ScanManga_nom.append(a.text.strip().lower())
                self.list_ScanManga_lien.append(a["href"])

        
    #Création csv initial
    def creer_csv(self):    
        
        filename = "Manga.csv"

        df1 = pd.DataFrame()
        df1["Nom"]=self.list_toonily_nom
        df1["Lien_Toonily"]=self.list_toonily_lien   
        #df1.to_csv("Toonily.csv",index=False)

        df2=pd.DataFrame()
        df2["Nom"]= self.list_MangaDemon_nom
        df2["Lien_MangaDemon"]=self.list_MangaDemon_lien 
        #df2.to_csv("MangaDemon.csv",index=False)
        
        df3=pd.DataFrame()
        df3["Nom"]=self.list_ScanManga_nom
        df3["Lien_ScanManga"]=self.list_ScanManga_lien 
        #df3.to_csv("ScanManga.csv",index=False)
        
        dfinter = pd.merge(df1,df2,on='Nom', how='outer').fillna(0)
        dfFin = pd.merge(dfinter, df3, on='Nom', how='outer').fillna(0)

        self.list_dernier_vu = [-1]*dfFin.shape[0]
        dfFin["Dernier_Vu"]=self.list_dernier_vu

        dfFin.to_csv(filename,index=False)
        
        
    #Utile pour changer le dernier vu
    def recreer_csv(self):
        filename = "Manga.csv"

        df = pd.DataFrame()
        
        df["Nom"]=self.list_nom
        df["Lien_Toonily"]=self.list_toonily_lien   
        df["Lien_MangaDemon"]=self.list_MangaDemon_lien 
        df["Lien_ScanManga"]=self.list_ScanManga_lien
        df["Dernier_Vu"]=self.list_dernier_vu
        
        # AAprès avoir fait une mise à jour
        df = df.sort_values(by='Nom').reset_index(drop=True)
        df.to_csv(filename,index=False)


    def creer_colonne(self):    

        filename = 'Manga.csv'
        df = pd.read_csv(filename)
        
        self.list_nom = df["Nom"].tolist()
        self.list_toonily_lien = df["Lien_Toonily"].tolist()
        self.list_MangaDemon_lien = df["Lien_MangaDemon"].tolist()
        self.list_ScanManga_lien=df["Lien_ScanManga"].tolist()
        self.list_dernier_vu=df["Dernier_Vu"].tolist()
        # ICI JE DOIS CHANGER POUR REMPLIR CHAQUE NOM DE MANGA PAR SITE + LIEN

        #print(f"Les données ont été lu dans {filename}")

    def mise_à_jour_toonily(self,ancienne_date):
        stop=False
        url = "https://toonily.com/"
        reponse = requests.get(url)
        if reponse.ok:
            soup = BeautifulSoup(reponse.text,"html.parser")
            animes = soup.find_all('div', class_="item-summary")
            for anime in animes :
                h3 = anime.find("h3",class_="h5")
                new_nom=h3.find("a").text.lower() 
                new_lien=h3.find("a")["href"]
                # SI VIDE c'est que UP
                date_str=anime.find('span', class_="post-on font-meta").text.strip()
                
                #Toutes les vraies date sont écrites comme cela (le jour même on recompare)
                pattern = re.compile(r'^.*day.*ago$')    
                if(',' in date_str):
                    #Autre moyen en plus de la méthode re
                    new_date =  datetime.strptime(date_str, '%b %d, %y')
                    if(new_date>=ancienne_date):
                        if(new_nom not in self.list_nom):
                            self.list_toonily_lien.append(new_lien)
                            self.list_nom.append(new_nom)
                            self.list_dernier_vu.append(-1)
                            self.list_MangaDemon_lien.append(0)
                            self.list_ScanManga_lien.append(0)
                        else:
                            if(self.list_toonily_lien[self.list_nom.index(new_nom)]=="0"):
                               self.list_toonily_lien[self.list_nom.index(new_nom)]=new_lien
                    else:
                        stop=True
                        return
                elif pattern.match(date_str):
                        new_date =  datetime.now()- timedelta(days=int(date_str[0]))
                        if(new_date>=ancienne_date):
                            if(new_nom not in self.list_nom):
                                self.list_toonily_lien.append(new_lien)
                                self.list_nom.append(new_nom)
                                self.list_dernier_vu.append(-1)
                                self.list_MangaDemon_lien.append(0)
                                self.list_ScanManga_lien.append(0)
                            else:
                                if(self.list_toonily_lien[self.list_nom.index(new_nom)]=="0"):
                                    self.list_toonily_lien[self.list_nom.index(new_nom)]=new_lien
                        else:
                            stop=True
                            return
                else:
                    if(new_nom not in self.list_nom):
                        self.list_toonily_lien.append(new_lien)
                        self.list_nom.append(new_nom)
                        self.list_dernier_vu.append(-1)
                        self.list_MangaDemon_lien.append(0)
                        self.list_ScanManga_lien.append(0)
                    else:
                        if(self.list_toonily_lien[self.list_nom.index(new_nom)]=="0"):
                            self.list_toonily_lien[self.list_nom.index(new_nom)]=new_lien
        i=2
        while(stop==False):
            url = "https://toonily.com/page/"+str(i)+"/"
            reponse = requests.get(url)
            if reponse.ok:
                soup = BeautifulSoup(reponse.text,"html.parser")
                animes = soup.find_all('div', class_="item-summary")
                for anime in animes :
                    h3 = anime.find("h3",class_="h5")
                    new_nom=h3.find("a").text.lower() 
                    new_lien=h3.find("a")["href"]
                    # SI VIDE c'est que UP
                    date_str=anime.find('span', class_="post-on font-meta").text.strip()
                    
                    #Toutes les vraies date sont écrites comme cela (le jour même on recompare)
                    pattern = re.compile(r'^.*day.*ago$')    
                    if(',' in date_str):
                        #Autre moyen en plus de la méthode re
                        new_date =  datetime.strptime(date_str, '%B %d, %Y')
                        if(new_date>=ancienne_date):
                            if(new_nom not in self.list_nom):
                                self.list_toonily_lien.append(new_lien)
                                self.list_nom.append(new_nom)
                                self.list_dernier_vu.append(-1)
                                self.list_MangaDemon_lien.append(0)
                                self.list_ScanManga_lien.append(0)
                            else:
                                if(self.list_toonily_lien[self.list_nom.index(new_nom)]=="0"):
                                    self.list_toonily_lien[self.list_nom.index(new_nom)]=new_lien
                        else:
                            stop=True
                            return
                    elif pattern.match(date_str):
                            new_date =  datetime.now()- timedelta(days=int(date_str[0]))
                            if(new_date>=ancienne_date):
                                if(new_nom not in self.list_nom):
                                    self.list_toonily_lien.append(new_lien)
                                    self.list_nom.append(new_nom)
                                    self.list_dernier_vu.append(-1)
                                    self.list_MangaDemon_lien.append(0)
                                    self.list_ScanManga_lien.append(0)
                                else:
                                    if(self.list_toonily_lien[self.list_nom.index(new_nom)]=="0"):
                                        self.list_toonily_lien[self.list_nom.index(new_nom)]=new_lien
                            else:
                                stop=True
                                return
                    else:
                        if(new_nom not in self.list_nom):
                            self.list_toonily_lien.append(new_lien)
                            self.list_nom.append(new_nom)
                            self.list_dernier_vu.append(-1)
                            self.list_MangaDemon_lien.append(0)
                            self.list_ScanManga_lien.append(0)
                        else:
                            if(self.list_toonily_lien[self.list_nom.index(new_nom)]=="0"):
                                self.list_toonily_lien[self.list_nom.index(new_nom)]=new_lien

            i=i+1   
    def mise_à_jour_MangaDemon(self,ancienne_date):  

        stop=False
        url = "https://mgdemon.org/updates"
        reponse = requests.get(url)
        if reponse.ok:
            soup = BeautifulSoup(reponse.text,"html.parser")
            animes = soup.find_all('div', class_="rightside boxsizing nomargpad")
            for anime in animes :
                h2 = anime.find("h2",class_="novel-title nomargpad")
                new_nom=h2.find("a")["title"].lower() 
                new_lien="https://mgdemon.org"+h2.find("a")["href"]
                # SI VIDE c'est que UP
                intermédiaire = anime.find('p', class_="nomargpad").text.strip()
                date_str=intermédiaire[8:len(intermédiaire)].strip()
                new_date = datetime.strptime(date_str, "%Y-%m-%d")
                if(new_date>=ancienne_date):
                    if(new_nom not in self.list_nom):
                        self.list_MangaDemon_lien.append(new_lien)
                        self.list_nom.append(new_nom)
                        self.list_dernier_vu.append(-1)
                        self.list_toonily_lien.append(0)
                        self.list_ScanManga_lien.append(0)
                    else:
                        if(self.list_MangaDemon_lien[self.list_nom.index(new_nom)]=="0"):
                            self.list_MangaDemon_lien[self.list_nom.index(new_nom)]=new_lien
                else:
                    stop=True
                    return
               
        i=2
        while(stop==False):
            url = "https://mgdemon.org/updates.php?list="+str(i)
            reponse = requests.get(url)
            if reponse.ok:
                soup = BeautifulSoup(reponse.text,"html.parser")
                animes = soup.find_all('div', class_="rightside boxsizing nomargpad")
                for anime in animes :
                    h2 = anime.find("h2",class_="novel-title nomargpad")
                    new_nom=h2.find("a")["title"].lower() 
                    new_lien="https://mgdemon.org"+h2.find("a")["href"]
                    # SI VIDE c'est que UP
                    intermédiaire = anime.find('p', class_="nomargpad").text.strip()
                    date_str=intermédiaire[8:len(intermédiaire)].strip()
                    new_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if(new_date>=ancienne_date):
                        if(new_nom not in self.list_nom):
                            self.list_MangaDemon_lien.append(new_lien)
                            self.list_nom.append(new_nom)
                            self.list_dernier_vu.append(-1)
                            self.list_toonily_lien.append(0)
                            self.list_ScanManga_lien.append(0)
                        else:
                            if(self.list_MangaDemon_lien[self.list_nom.index(new_nom)]=="0"):
                                self.list_MangaDemon_lien[self.list_nom.index(new_nom)]=new_lien
                    else:
                        stop=True
                        return

            i=i+1   
    def mise_à_jour_ScanManga(self):
        url = "https://www.scan-manga.com/?po"
        # Options pour Chrome (comme le mode headless)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Lance Chrome en mode headless (sans interface graphique)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36')

        # Initialisation du driver
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        page_source = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(page_source, "html.parser")

        pattern = re.compile(r'^top.*listing$')    
        animes = soup.find_all('div', class_=pattern)
        for anime in animes :
            a = anime.find('a',class_="atop")
            if(a is not None):
                #Strip c'est pour enlever les espaces
                new_nom=a.text.strip().lower()
                new_lien=a["href"]
                #Convertit en date classique (de base c'est en Unix)
                if(new_nom not in self.list_nom):
                    self.list_ScanManga_lien.append(new_lien)
                    self.list_nom.append(new_nom)
                    self.list_dernier_vu.append(-1)
                    self.list_toonily_lien.append(0)
                    self.list_MangaDemon_lien.append(0)
                else:
                    if(self.list_ScanManga_lien[self.list_nom.index(new_nom)]=="0"):
                        self.list_ScanManga_lien[self.list_nom.index(new_nom)]=new_lien
        
    def mise_à_jour(self,ancienne_date):

        self.mise_à_jour_toonily(ancienne_date)
        #Ils ont changé le site je suis bz
        self.mise_à_jour_MangaDemon(ancienne_date)
        self.mise_à_jour_ScanManga()

"""
bdd=BDDManga()
bdd.mise_à_jour_ScanManga()

bdd=BDDManga()
bdd.creer_bdd_MangaDemon()
bdd.creer_bdd_toonily()
bdd.creer_bdd_ScanManga()
bdd.creer_csv()
"""