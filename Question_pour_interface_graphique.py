import tkinter as tk
import webbrowser
from tkinter import messagebox
from datetime import datetime
import pandas as pd
from fuzzywuzzy import process

# Import des modules fictifs pour la démonstration
# Assure-toi que ces imports fonctionnent correctement dans ton environnement
from voiranime import BDDVoirAnime
from trouver_lien_voiranime_pour_interface_graphique import lien_final as LFV

from manga import BDDManga
from trouver_lien_toonily import lien_final as LFT
from trouver_lien_mangademon import lien_final as LFMD
from trouver_lien_scanmanga import lien_final as LFSM

# Variables globales pour gérer l'état
filename = 'Date.csv'
df = pd.read_csv(filename)
maintenant = datetime.now()

def clear_widgets(window):
    # Supprimer tous les widgets existants
    for widget in window.winfo_children():
        widget.destroy()

def show_anime_screen(window):
    clear_widgets(window)
    tk.Label(window, text="Vous avez choisi Animé. Entrez le nom :").pack(pady=10)
    
    nom_entry = tk.Entry(window)
    nom_entry.pack(pady=10)
    
    def process_anime():
        
        nom = nom_entry.get().strip().lower()
        ancienne_date = datetime.strptime(df.loc[0, "Date_Anime"], '%d/%m/%Y')        
        bdd = BDDVoirAnime()
        bdd.creer_colonne()
        bdd.mise_à_jour(ancienne_date)
        bdd.tri()
            
        # Mettre à jour la date sur le csv
        df.loc[0, "Date_Anime"] = maintenant.strftime('%d/%m/%Y')       
        df.to_csv(filename, index=False)

        if nom in bdd.List_Nom:
            LFV(window,bdd.List_Lien[bdd.List_Nom.index(nom)], bdd)
        else:
            noms_proches = trouver_mots_proches(nom, bdd.List_Nom)
            clear_widgets(window)
            tk.Label(window, text="Animés les plus probables :").pack(pady=10)
            for i, (mot, _) in enumerate(noms_proches, start=1):
                tk.Label(window, text=f"{i}. {mot}").pack(pady=10)

            tk.Label(window,text="Choisis en donnant son numéro dans la liste\n (0 c'est aucun le bon)")
            # Champ de texte pour entrer le numéro
            num_entry = tk.Entry(window)
            num_entry.pack(pady=10)
                
            def process_choice():
                rep = num_entry.get().strip()
                if rep == "0":
                    tk.Label(window, text="Tu n'as pas trouvé ton animé.").pack(pady=10)
                else:
                    index = int(rep) - 1
                    if 0 <= index < len(noms_proches):
                        nom_proche = noms_proches[index][0]
                        LFV(window,bdd.List_Lien[bdd.List_Nom.index(noms_proches[index][0])],bdd)
                    else:
                        tk.Label(window, text="Numéro invalide.").pack(pady=10)
            tk.Button(window, text="Choisir", command=process_choice).pack(pady=10)             
    tk.Button(window, text="Valider", command=process_anime).pack(pady=10)
    
def show_scan_screen(window):
    clear_widgets(window)
    tk.Label(window, text="Vous avez choisi Scan. Entrer le nom du scan").pack(pady=10)
    nom_entry = tk.Entry(window)
    nom_entry.pack(pady=10)
    def process_scan():
        nom = nom_entry.get().strip().lower()
        ancienne_date = datetime.strptime( df.loc[0, "Date_Manga"], '%d/%m/%Y')  
        bdd2 = BDDManga()
        bdd2.creer_colonne() 
        bdd2.mise_à_jour(ancienne_date) 

        #On met à jour la date sur le csv
        df.loc[0, "Date_Manga"] = maintenant.strftime('%d/%m/%Y')
        df.to_csv(filename,index=False)
        # C'est après le if après la fonction mais on doit la mettre la pour l'appeler
        def suite(nom):
            list_episode_scanmanga = []
            list_episode_mangademon=[]
            list_episode_toonily=[]
            #Toonily
            if(bdd2.List_Toonily_Lien[bdd2.List_Nom.index(nom)]!="0"):
                url1=bdd2.List_Toonily_Lien[bdd2.List_Nom.index(nom)]
                list_episode_toonily=LFT(url1,bdd2)
            #MangaDemon
            if(bdd2.List_MangaDemon_Lien[bdd2.List_Nom.index(nom)]!="0"):
                url2=bdd2.List_MangaDemon_Lien[bdd2.List_Nom.index(nom)]
                list_episode_mangademon=LFMD(url2,bdd2)
            #ScanManga
            if(bdd2.List_ScanManga_Lien[bdd2.List_Nom.index(nom)]!="0"):
                url3=bdd2.List_ScanManga_Lien[bdd2.List_Nom.index(nom)]
                list_episode_scanmanga,list_numéro_chapitre_ScanManga=LFSM(url3,bdd2)
                

            list_max=max(list_episode_mangademon,list_episode_toonily,list_episode_scanmanga,key=len)
            if(list_max==list_episode_toonily):
                url=url1
                dernier_vu=str(bdd2.List_Dernier_Vu[bdd2.List_Toonily_Lien.index(url1)])
            elif(list_max==list_episode_mangademon):
                url=url2
                dernier_vu=str(bdd2.List_Dernier_Vu[bdd2.List_MangaDemon_Lien.index(url2)])
            else:
                url=url3
                dernier_vu=str(bdd2.List_Dernier_Vu[bdd2.List_ScanManga_Lien.index(url3)])
            #Si on a déjà vu des épisodes
            clear_widgets(window)
            def continuer_apres_questionmanga(num):
                print("Test4")
                clear_widgets(window)
                if(num==-1):
                    tk.Label(window,text="Plus de scan pour vous, vous avez tout lu").pack(pady=10)
                    bdd2.recreer_csv()
                #On a aussi un minimum car pas pareil que le num du chapitre (c'est à l'envers)
                else:
                    if len(list_episode_toonily) >= num:
                        webbrowser.open(url1+"chapter-"+str(num)+"/")
                    if len(list_episode_mangademon)>= num:
                        webbrowser.open(url2[0:len(url2)-5]+"/chapter/"+str(num)+url2[len(url2)-5:len(url2)])
                    if len(list_episode_scanmanga)>=num:
                        try:
                            #Cela peut bug trop de truc bizarre sur le site scan manga
                            webbrowser.open(list_episode_scanmanga[list_numéro_chapitre_ScanManga.index(str(num))])
                        except:
                            tk.Label(window, text="Erreur: Numéro de chapitre hors des limites pour ScanManga.").pack(pady=10)
                    changer_dernier_épisode(bdd2,nom,num)  
            num = questionmanga(window,list_max,dernier_vu,continuer_apres_questionmanga)

            
        if(nom not in bdd2.List_Nom):
            noms_proches = trouver_mots_proches(nom, bdd2.List_Nom)
            clear_widgets(window)
            tk.Label(window, text="Animés les plus probables :").pack(pady=10)
            for i, (mot, _) in enumerate(noms_proches, start=1):
                tk.Label(window, text=f"{i}. {mot}").pack(pady=10)

            tk.Label(window,text="Choisis en donnant son numéro dans la liste\n (0 c'est aucun le bon)").pack(pady=10)
            # Champ de texte pour entrer le numéro
            num_entry = tk.Entry(window)
            num_entry.pack(pady=10)
            def process_choice():
                rep = num_entry.get().strip()
                clear_widgets(window)
                if rep == "0":
                    tk.Label(window, text="Tu n'as pas trouvé ton animé.").pack(pady=10)
                    bdd2.recreer_csv()
                    return
                else:
                    nom=noms_proches[int(rep)-1][0]  
                    suite(nom)
            tk.Button(window, text="Choisir", command=process_choice).pack(pady=10)  
        else:
            suite(nom)

        
    tk.Button(window, text="Valider", command=process_scan).pack(pady=10)   
    
        
        
def show_film_screen(window):
    clear_widgets(window)
    tk.Label(window, text="Vous avez choisi Film.").pack(pady=10)
    # Ici tu peux appeler ta fonction pour gérer les films

def questionmanga(window,list_episode,dernier_vu,callback):
    def choisir_épisode():            
        tk.Label(window,text="Il y a "+str(len(list_episode))+" chapitre. Lequelles veux tu lires ?").pack(pady=10)
        numero_entrée = tk.Entry(window)
        numero_entrée.pack(pady=10)
        def choisir_ep():
            num=numero_entrée.get().strip() 
            callback(int(num))                   
        tk.Button(window,text="Valider",command=choisir_ep).pack(pady=10)  
    if(len(list_episode)==0):
       callback(-1)
       return
    if(dernier_vu!=str(len(list_episode)) and dernier_vu!="-1") :
        def episode_suivant():
            callback(int(dernier_vu)+1)           
        tk.Label(window, text="Vous vous êtes arrétés à l'épisode "+dernier_vu).pack(pady=10)
        tk.Button(window,text = "Voulez vous regarder le prochain ?",command=episode_suivant).pack(pady=10)
        tk.Button(window,text="Voulez vous choisir un autre épisode ?",command=choisir_épisode).pack(pady=10)                    
    #Ca passe ici
    elif(dernier_vu==str(len(list_episode))):
        def arretez():
           callback(-1)
        tk.Label(window, text="Vous avez fini la série voulez vous quand même lire un chapitre ?").pack(pady=10)
        tk.Button(window,text = "Voulez vous arretez ?",command=arretez).pack(pady=10)
        tk.Button(window,text="Voulez vous choisir un autre épisode ?",command=choisir_épisode).pack(pady=10)                    
    else:
        choisir_épisode()


def changer_dernier_épisode(bdd,nom,numéro):
    bdd.List_Dernier_Vu[bdd.List_Nom.index(nom)]=numéro
    bdd.recreer_csv()

def trouver_mots_proches(mot, base_de_donnees, nombre_de_resultats=5):
    resultats = process.extract(mot, base_de_donnees, limit=nombre_de_resultats)
    return resultats

def main():
    window = tk.Tk()
    window.title("Choix de contenu")
    window.geometry("600x400")

    
    tk.Button(window, text="Animé", command=lambda: show_anime_screen(window)).pack(padx=20, pady=10)
    tk.Button(window, text="Scan", command=lambda: show_scan_screen(window)).pack(padx=20, pady=10)
    tk.Button(window, text="Film", command=lambda: show_film_screen(window)).pack(padx=20, pady=10)
    
    window.mainloop()

if __name__ == "__main__":
    main()
