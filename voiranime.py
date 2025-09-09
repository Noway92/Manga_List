import requests
from bs4 import BeautifulSoup
import sys
import io
import csv
from datetime import datetime, timedelta
import re
import pandas as pd
#Bug d'écriture sinon
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

#LE TOUT EST FAIT SANS PANDAS ET NUMPY

class BDDVoirAnime:
    def __init__(self):
        self.list_nom=[]
        self.list_lien =[]
        self.list_dernier_vu=[]
    
    @property
    def List_Nom(self):
        return self.list_nom
    
    @property
    def List_Dernier_Vu(self):
        return  self.list_dernier_vu
    
    
    @property
    def List_Lien(self):
        return  self.list_lien
    

    def creer_bdd(self): 
        list_lien = []
        list_nom=[]
        list_dernier_vu=[]
        nb_pages = 0

        # Ici on fait la première boucle pour récupérer le nombres de page + fait la page 1 
        url = "https://v5.voiranime.com/liste-danimes/?filter=subbed"
        reponse = requests.get(url)
        if reponse.ok:
            soup = BeautifulSoup(reponse.text,"html.parser")
            nb_pages = soup.find('span', class_="pages").text.split()[-1]
            animes = soup.find_all('div', class_="col-12 badge-pos-1")
            for anime in animes :
                inter = anime.find('div', class_="post-title font-title")
                h3 = inter.find("h3")
                self.list_nom.append(h3.text[1:-1].lower())
                self.list_lien.append(h3.find("a")["href"])
                self.list_dernier_vu.append("-1")

        #for i in range(2,5):
        for i in range(2,int(nb_pages)+1):
            url = "https://v5.voiranime.com/liste-danimes/page/"+str(i)+"/?filter=subbed"
            reponse = requests.get(url)
            if reponse.ok:
                soup = BeautifulSoup(reponse.text,"html.parser")
                animes = soup.find_all('div', class_="col-12 badge-pos-1")
                for anime in animes :
                    inter = anime.find('div', class_="post-title font-title")
                    h3 = inter.find("h3")
                    self.list_nom.append(h3.text[1:-1].lower())
                    self.list_lien.append(h3.find("a")["href"])
                    self.list_dernier_vu.append("-1")

        
        #On a tous les animé dans la liste
    def creer_csv(self):      
        list1=self.list_nom
        list2=self.list_lien
        list3=self.list_dernier_vu
        # Assurez-vous que les deux listes ont la même longueur
        assert len(list1) == len(list2)==len(list3), "Les deux listes doivent avoir la même longueur"

        # Nom du fichier CSV
        filename = 'voiranime.csv'
        # Ouvrir le fichier en mode écriture
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)            
            # Écrire l'en-tête des colonnes (optionnel)
            csvwriter.writerow(['Nom', 'lien',"DernierVu"])            
            # Écrire les lignes des listes
            for i in range(len(list1)):
                csvwriter.writerow([list1[i], list2[i],list3[i]])

        #print(f"Les données ont été écrites dans {filename}")



    def creer_colonne(self):    

        filename = 'voiranime.csv'
        # Ouvrir le fichier CSV en mode lecture
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            # Créer un objet reader
            csvreader = csv.DictReader(csvfile)

            # Lire les lignes du fichier CSV et ajouter les données aux listes
            for row in csvreader:
                self.list_nom.append(row["Nom"])
                self.list_lien.append(row["lien"])
                self.list_dernier_vu.append(row["DernierVu"])
        #print(f"Les données ont été lu dans {filename}")
    
    def mise_à_jour(self,ancienne_date):
        stop=False
        url = "https://v5.voiranime.com/?filter=subbed"
        reponse = requests.get(url)
        if reponse.ok:
            soup = BeautifulSoup(reponse.text,"html.parser")
            animes = soup.find_all('div', class_="col-12 col-md-6 badge-pos-1")
            for anime in animes :
                inter = anime.find('div', class_="post-title font-title")
                h3 = inter.find("h3")
                new_nom=h3.text[1:-1].lower() #Je pourrais utiliser .strip() aussi
                new_lien=h3.find("a")["href"]
                date_str=anime.find('span', class_="post-on font-meta").text.strip()
                
                #Toutes les vraies date sont écrites comme cela (le jour même on recompare)
                pattern = re.compile(r'^.*day.*ago$')    
                if(',' in date_str):
                    #Autre moyen en plus de la méthode re
                    new_date =  datetime.strptime(date_str, '%B %d, %Y')
                    if(new_date>=ancienne_date):
                        if(new_nom not in self.list_nom):
                            self.list_lien.append(new_lien)
                            self.list_nom.append(new_nom)
                            self.list_dernier_vu.append("-1")
                    else:
                        stop=True
                        return
                elif pattern.match(date_str):
                        new_date =  datetime.now()- timedelta(days=int(date_str[0]))
                        if(new_date>=ancienne_date):
                            if(new_nom not in self.list_nom):
                                self.list_lien.append(new_lien)
                                self.list_nom.append(new_nom)
                                self.list_dernier_vu.append("-1")
                        else:
                            stop=True
                            return
                else:
                    if(new_nom not in self.list_nom):
                            self.list_lien.append(new_lien)
                            self.list_nom.append(new_nom)
                            self.list_dernier_vu.append("-1")
                
                
        i=2
        while(stop==False):
            url = "https://v5.voiranime.com/page/"+str(i)+"/?filter=subbed"
            reponse = requests.get(url)
            if reponse.ok:
                soup = BeautifulSoup(reponse.text,"html.parser")
                animes = soup.find_all('div', class_="col-12 col-md-6 badge-pos-1")
                for anime in animes :
                    inter = anime.find('div', class_="post-title font-title")
                    h3 = inter.find("h3")
                    new_nom=h3.text[1:-1].lower()
                    new_lien=h3.find("a")["href"]

                    date_str=anime.find('span', class_="post-on font-meta").text.strip()
                    pattern = re.compile(r'^.*day.*ago$') 
                    
                    #Toutes les vraies date sont écrites comme cela (le jour même on recompare)
                    if(',' in date_str):
                        #Autre moyen en plus de la méthode re
                        new_date =  datetime.strptime(date_str, '%B %d, %Y')
                        if(new_date>=ancienne_date):
                            if(new_nom not in self.list_nom):
                                self.list_lien.append(new_lien)
                                self.list_nom.append(new_nom)
                                self.list_dernier_vu.append("-1")
                        else:
                            stop=True
                            return
                    elif pattern.match(date_str):
                        new_date =  datetime.now()- timedelta(days=int(date_str[0])) 
                        if(new_date>=ancienne_date):
                            if(new_nom not in self.list_nom):
                                self.list_lien.append(new_lien)
                                self.list_nom.append(new_nom)
                                self.list_dernier_vu.append("-1")
                        else:
                            stop=True
                            return
                    else:
                        if(new_nom not in self.list_nom):
                                self.list_lien.append(new_lien)
                                self.list_nom.append(new_nom)
                                self.list_dernier_vu.append("-1")
            i=i+1
    def tri(self):
        #Juste pour trier
        df = pd.DataFrame({
            'lien': self.list_lien,
            'nom': self.list_nom,
            'dernier_vu': self.list_dernier_vu
        })
            
        # Trier le DataFrame en fonction de la colonne 'nom'
        df_sorted = df.sort_values(by='nom').reset_index(drop=True)
        self.list_lien = df_sorted['lien'].tolist()
        self.list_nom = df_sorted['nom'].tolist()
        self.list_dernier_vu = df_sorted['dernier_vu'].tolist()

"""
bdd=BDDVoirAnime()
bdd.creer_bdd()
bdd.creer_csv()


class="page-listing-item" : LIGNE
class = "item-summary": CELLULE



https://v5.voiranime.com/anime/my-wife-has-no-emotion/my-wife-has-no-emotion-01-vostfr/
https://v5.voiranime.com/anime/my-wife-has-no-emotion/my-wife-has-no-emotion-02-vostfr/

https://v5.voiranime.com/anime/boku-no-hero-academia-7/boku-no-hero-academia-7-11-vostfr/

Il faut donc capter que c'est le nom de l'animé 2 fois d'affilée avec le numéro 

Je prend le nom de tous les animés de voiranime
Je cherche celui que je veux (je dis si il est la ou pas )
si oui je demande l'episode

"""