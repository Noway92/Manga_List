from datetime import datetime
import pandas as pd
from voiranime import BDDVoirAnime
from manga import BDDManga
from trouver_lien_voiranime import lien_final as LFV
from trouver_lien_toonily import lien_final as LFT
from trouver_lien_mangademon import lien_final as LFMD
from trouver_lien_scanmanga import lien_final as LFSM
import os
from fuzzywuzzy import process

def main():
    print("Cherchez vous un animé/scan/film (1/2/3)")
    rep = input().strip()
    maintenant = datetime.now()
    filename = 'Date.csv'
    df = pd.read_csv(filename)
    if rep=="1" :
        ancienne_date =  datetime.strptime(df.loc[0, "Date_Anime"], '%d/%m/%Y')        
        print("Donner le nom")
        nom=input().lower()
        bdd = BDDVoirAnime()
        bdd.creer_colonne()
        #On met à jour notre bdd
        bdd.mise_à_jour(ancienne_date)
        #On l'a trié
        bdd.tri()
        
        #On met à jour la date sur le csv
        df.loc[0, "Date_Anime"] = maintenant.strftime('%d/%m/%Y')       
        df.to_csv(filename,index=False)

        if(nom in bdd.List_Nom):
            LFV(bdd.List_Lien[bdd.List_Nom.index(nom)],bdd)
        else:
            noms_proches=trouver_mots_proches(nom, bdd.List_Nom)
            print("Animés les plus probables :")
            for i, (mot, _) in enumerate(noms_proches, start=1):
                print(f"{i}. {mot}")
            print("\nChoisis en donnant son numéro dans la liste (0 c'est aucun le bon)")
            rep = input()
            if(rep==0):
                print("Tu n'as pas trouvé ton animé")
            else:
                LFV(bdd.List_Lien[bdd.List_Nom.index(noms_proches[int(rep)-1][0])],bdd)
        #Ici on a le csv recreer pour dernier vu + pour mise à jour
        bdd.creer_csv()
    elif rep=="2" :
        ancienne_date = datetime.strptime( df.loc[0, "Date_Manga"], '%d/%m/%Y')    
        print("Donner le nom sans faute d'orthographe")
        nom=input().lower()
        bdd2 = BDDManga()
        bdd2.creer_colonne() 
        bdd2.mise_à_jour(ancienne_date) 

        #On met à jour la date sur le csv
        df.loc[0, "Date_Manga"] = maintenant.strftime('%d/%m/%Y')
        df.to_csv(filename,index=False)

        os.system('cls')
        if(nom not in bdd2.List_Nom):
            noms_proches=trouver_mots_proches(nom, bdd2.List_Nom)
            print("Scan les plus probables :")
            for i, (mot, _) in enumerate(noms_proches, start=1):
                print(f"{i}. {mot}")
            print("\nChoisis en donnant son numéro dans la liste (0 c'est aucun le bon)")
            rep = input()
            if(rep=="0"):
                print("Tu n'as pas trouvé ton scan")
                #Ici on a le csv recréé pour dernier vu + pour mise à jour
                bdd2.recreer_csv()
                return
            else:
                nom=noms_proches[int(rep)-1][0]            
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
            
        num = int(questionmanga(list_max,dernier_vu))
        if(num==-1):
            print("Plus d'épisodes pour vous, vous avez tout lu")
        #On a aussi un minimum car pas pareil que le num du chapitre (c'est à l'envers)
        else:
            if len(list_episode_toonily) >= num:
                print(url1+"chapter-"+str(num)+"/")
            if len(list_episode_mangademon)>= num:
                print(url2[0:len(url2)-5]+"/chapter/"+str(num)+url2[len(url2)-5:len(url2)])
            if len(list_episode_scanmanga)>=num:
                #Cela peut bug trop de truc bizarre sur le site scan manga
                print(list_episode_scanmanga[list_numéro_chapitre_ScanManga.index(str(num))])
            changer_dernier_épisode(bdd2,nom,num)    

        #Ici on a le csv recréé pour dernier vu + pour mise à jour
        bdd2.recreer_csv()
    else :
        print("Donner le nom sans faute d'orthographe")
        nom=input().lower()


            
def questionmanga(list_episode,dernier_vu):
    if(dernier_vu!=str(len(list_episode)) and dernier_vu!="-1") :
        print("Vous vous êtes arrétés au chapitre "+dernier_vu+"\nVoulez vous lire le prochain ? (1)\nVoulez vous choisir un autre chapitre ? (2)")
        rep3= input()
        if(rep3=="1"):
            num=str(int(dernier_vu)+1)
            os.system('cls')
            
            return int(num)
                
        #Si on a finit la série                        
    elif(dernier_vu==str(len(list_episode))):
        print("Vous avez fini la série voulez vous quand même lire un chapitre ? (Y/N)")
        rep3 = input()
        if(rep3!="Y"):
            return -1

    if(len(list_episode)==0):
        return -1
    #Si on veut juste choisir un épisode  
    print("Il y a "+str(len(list_episode))+" chapitre. Lequel veux tu lires ?")
    num = input()
    os.system('cls')
    while(int(num)>len(list_episode) or int(num)<1):
        print("Lequel veux tu lire ? (plus petit que "+str(len(list_episode))+")")
        num = input()   
        os.system('cls') 
        
    return int(num)

def changer_dernier_épisode(bdd,nom,numéro):
    bdd.List_Dernier_Vu[bdd.List_Nom.index(nom)]=numéro
    bdd.recreer_csv()

def trouver_mots_proches(mot, base_de_donnees, nombre_de_resultats=5):
    resultats = process.extract(mot, base_de_donnees, limit=nombre_de_resultats)
    return resultats   

if __name__ == "__main__":
    main()

"""
A VOIR 

_ savoir quel est le dernier épisode que l'on a regardé et le dire
_ creer un index avce des poids si pas exact le mot


"""