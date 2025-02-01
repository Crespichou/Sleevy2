import sqlite3
import pandas as pd

file_path = 'PPG_data_combined.xlsx'
df = pd.read_excel(file_path)
colonne_valeurs = 'Valeur Série RankedRivals5'
valeurs = df[colonne_valeurs].dropna().tolist()

def afficher_donnees():
    """Affiche les données d'une table."""
    try:
        #connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien tablette Antoine
        connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien PC Antoine
        print("Connexion réussie.")
        
        curseur = connexion.cursor()
        
        #Mettre bonne requête
        requete = "SELECT * FROM coach"
        curseur.execute(requete)

        resultat = curseur.fetchall()

        if resultat:
            for row in resultat:
                print(row)  
        else:
            print("La table est vide.")
        
        connexion.close()
        
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)

def modifier_donnees():
    """Envoie une requête d'insertion dans une table."""
    try:
        #connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien PC Antoine
        connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien tablette Antoine
        print("Connexion réussie.")
        
        curseur = connexion.cursor()
        
        #Mettre bonne requête
        requete = """
        INSERT INTO sleevyppg (sessionid, valeurppg, dateppg, heureppg, idjoueur)
        VALUES (?, ?, ?, ?, ?)
        """
        #Requete pour insérer les données excel
        #INSERT INTO sleevyppg (sessionid, valeurppg, dateppg, heureppg, idjoueur)
        #VALUES (?, ?, ?, ?, ?)
        curseur.executemany(requete, [(5, valeur, '03/10', '16:17' , 1) for valeur in valeurs])
        #curseur.execute(requete)
        

        connexion.commit()
        print("Insertion réussie dans la table.")
        
        connexion.close()
        
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)

import sqlite3

def afficher_valeurs_en_une_ligne():
    """Affiche les valeurs de la colonne 'valeurppg' sous forme de liste dans une seule ligne."""
    try:
        connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien tablette Antoine
        #connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\BDD\Sleevy.db") #Lien PC Antoine
        print("Connexion réussie.")
        
        curseur = connexion.cursor()
        
        # Exécution de la requête pour récupérer les valeurs sous forme de liste
        requete = "SELECT GROUP_CONCAT(valeurppg) FROM sleevyppg WHERE sessionid=2"
        curseur.execute(requete)
        resultat = curseur.fetchone()
        
        if resultat and resultat[0]:
            # Affiche les valeurs sous forme de liste séparées par des virgules
            print("Liste des valeurs :")
            print(resultat[0])
        else:
            print("La table est vide ou aucune donnée n'a été trouvée.")
        
        connexion.close()
        
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)


#afficher_valeurs_en_une_ligne()
modifier_donnees()  
#afficher_donnees() 
