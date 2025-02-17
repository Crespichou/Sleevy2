import sqlite3
import pandas as pd

file_path = 'EMG_data.xlsx'
df = pd.read_excel(file_path)
colonne_valeurs = 'rivalsrapide4(mort5 méthode 2, dps fin)'
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
        INSERT INTO sleevyemg (idjoueur, session_id, valeuremg, dateemg)
        VALUES (?, ?, ?, ?)
        """
        #Requete pour insérer les données excel
        #INSERT INTO sleevyppg (sessionid, valeurppg, dateppg, heureppg, idjoueur)
        #VALUES (?, ?, ?, ?, ?)
        curseur.executemany(requete, [(1, 2,  valeur, '07/01') for valeur in valeurs])
        #curseur.execute(requete)
        

        connexion.commit()
        print("Insertion réussie dans la table.")
        
        connexion.close()
        
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)

import sqlite3

def afficher_valeurs_en_une_ligne(): 
    """Affiche les valeurs de la colonne 'valeurppg' sous forme de liste dans une seule ligne.
    Sélectionne une première fois tous les session_id d'un joueur et puis affiche en liste chacune de ses games.
    """
    try:
        connexion = sqlite3.connect(r"C:\Users\cresp\OneDrive\Documents\Sleevy\Sleevy2\BDD\Sleevy.db")  # Lien tablette Antoine
        #connexion = sqlite3.connect(r"C:\Users\cresp\Documents\Sleevy\Sleevy2\BDD\Sleevy.db")  # Lien PC Antoine
        print("Connexion réussie.")
        
        curseur = connexion.cursor()
        
        # Requête pour récupérer tous les session_id distincts associés à idjoueur = 1
        requete_session_ids = """
        SELECT DISTINCT session_id
        FROM sleevyppg
        WHERE idjoueur = 1;
        """

        curseur.execute(requete_session_ids)
        session_ids = curseur.fetchall()  # Cela récupère tous les session_id distincts.

        # Pour chaque session_id distinct, exécute une nouvelle requête GROUP_CONCAT
        for session_id in session_ids:
            session_id_val = session_id[0]  # Récupère le session_id (première colonne de la ligne retournée)

            # Création de la requête GROUP_CONCAT pour ce session_id
            requete_valeurs = """
            SELECT GROUP_CONCAT(valeurppg) 
            FROM sleevyppg 
            WHERE idjoueur = 1 AND session_id = ?
            GROUP BY session_id;
            """
    
            curseur.execute(requete_valeurs, (session_id_val,))
            result = curseur.fetchone()  # Récupère la liste de valeurs pour ce session_id

            if result:
                print(f"Session {session_id_val}: {result[0]}")  # Affiche les valeurs concaténées
            else:
                print(f"Session {session_id_val}: Pas de valeurs.")
        
        # Lignes inutiles commentées :
        # curseur.execute(requete)
        # resultat = curseur.fetchone()
        # if resultat and resultat[0]:
        #     Affiche les valeurs sous forme de liste séparées par des virgules
        #     print("Liste des valeurs :")
        #     print(resultat[0])
        # else:
        #     print("La table est vide ou aucune donnée n'a été trouvée.")
        
        connexion.close()
    
    except sqlite3.Error as e:
        print("Problème avec le fichier :", e)



#afficher_valeurs_en_une_ligne()
modifier_donnees()  
#afficher_donnees() 
