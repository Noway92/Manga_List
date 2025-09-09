#On associe l'anime avec le lien que l'on aura : 
import requests
from bs4 import BeautifulSoup
import sys
import io
from voiranime import BDDVoirAnime
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

        #Si on a déjàà vu des épisodes
        dernier_vu=bdd.List_Dernier_Vu[bdd.List_Lien.index(url)]
        if(dernier_vu!=str(len(episodes)) and dernier_vu!="-1") :
            print("Vous vous êtes arrétés à l'épisode "+dernier_vu+"\nVoulez vous regarder le prochain ? (1)\nVoulez vous choisir un autre épisode ? (2)")
            rep3= input()
            if(rep3=="1"):
                num=str(int(dernier_vu)+1)
                os.system('cls')
                print(list_episode[len(list_episode)-int(num)])
                changer_dernier_épisode(bdd,url,num)
                return
                
        #Si on a finit la série                        
        elif(dernier_vu==str(len(episodes))):
            print("Vous avez fini la série voulez vous quand même regarder un épisode ? (Y/N)")
            rep3 = input()
            if(rep3!="Y"):
                return

        if(len(list_episode)==0):
           return
        #Si on veut juste choisir un épisode  
        print("Il y a "+str(len(list_episode))+" épisodes. Lequelles veux tu regarder ?")
        num = input()
        os.system('cls')
        while(int(num)>len(list_episode) or int(num)<1):
            print("Lequelles veux tu regarder ? (plus petit que "+str(len(list_episode))+")")
            num = input()   
            os.system('cls') 
        
        print(list_episode[len(list_episode)-int(num)])
        changer_dernier_épisode(bdd,url,num)


def changer_dernier_épisode(bdd,url,numéro):
    bdd.List_Dernier_Vu[bdd.List_Lien.index(url)]=numéro
