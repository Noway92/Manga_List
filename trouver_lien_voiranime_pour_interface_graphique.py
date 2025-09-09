#On associe l'anime avec le lien que l'on aura : 
import requests
from bs4 import BeautifulSoup
import sys
import io
from voiranime import BDDVoirAnime
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pandas as pd
from fuzzywuzzy import process
import webbrowser


#Bug d'écriture sinon
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def lien_final(window,url,bdd):
    from Question_pour_interface_graphique import clear_widgets
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
            clear_widgets(window)
            tk.Label(window, text="Vous vous êtes arrétés à l'épisode "+dernier_vu).pack(pady=10)
            tk.Button(window,text = "Voulez vous regarder le prochain ?",command=lambda: episode_suivant(window,dernier_vu,bdd,url,list_episode)).pack(pady=10)
            tk.Button(window,text="Voulez vous choisir un autre épisode ?",command=lambda: choisir_épisode(window,bdd,url,list_episode)).pack(pady=10)

        else:
            choisir_épisode(window,bdd,url,list_episode)

def episode_suivant(window,dernier_vu,bdd,url,list_episode):
    from Question_pour_interface_graphique import clear_widgets
    num=str(int(dernier_vu)+1)
    clear_widgets(window)
    webbrowser.open(list_episode[len(list_episode)-int(num)])
    tk.Label(window,text="Vous avez terminé").pack(pady=10)
    changer_dernier_épisode(bdd,url,num)
                

def choisir_épisode(window,bdd,url,list_episode): 
    from Question_pour_interface_graphique import clear_widgets
    if(len(list_episode)==0):
        return
    #Si on veut juste choisir un épisode  
    clear_widgets(window)
    tk.Label(window, text="Il y a "+str(len(list_episode))+" épisodes. Lequelle veux tu regarder ?").pack(pady=10)
    episode = tk.Entry(window)
    episode.pack(pady=10)
    def fin():
        num=episode.get().strip()
        clear_widgets(window)
        webbrowser.open(list_episode[len(list_episode)-int(num)])
        tk.Label(window,text="Vous avez terminé").pack(pady=10)
        

        changer_dernier_épisode(bdd,url,num)
    # On ne doit pas mettre les () pour fin car s'appelle directement sinon
    tk.Button(window, text="Valider", command=fin).pack(pady=10)
    
    


def changer_dernier_épisode(bdd,url,numéro):
    bdd.List_Dernier_Vu[bdd.List_Lien.index(url)]=numéro
    bdd.creer_csv()
