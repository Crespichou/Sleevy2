import openpyxl
import numpy as np

from Projet.BPM_Pattern_Creation2 import (
    load_data,
    calculate_reference_mean,
    calculate_variabilities,
    group_datasets_by_variability
)

file_path = 'PPG_data_combined.xlsx'
sheet_names = ['Sheet2']
columns_per_sheet = [[14]]  # Colonne contenant les nouvelles données

# Charger les nouveaux jeux de données
new_data = load_data(file_path, sheet_names, columns_per_sheet)
new_dataset = {
    'NewRanked': new_data['Sheet2'][0]
}

# Charger les données existantes
existing_file_path = 'PPG_data_combined.xlsx'
existing_sheet_names = ['Sheet1', 'Sheet2']
existing_columns_per_sheet = [[2, 4, 6, 8, 10, 12, 14, 16], [10, 11, 12, 13]]

existing_data = load_data(existing_file_path, existing_sheet_names, existing_columns_per_sheet)
existing_datasets = {
    'Ranked1': existing_data['Sheet1'][0], 'Ranked2': existing_data['Sheet1'][1],
    'Ranked3': existing_data['Sheet1'][2], 'Ranked4': existing_data['Sheet1'][3],
    'Ranked5': existing_data['Sheet1'][4], 'Ranked6': existing_data['Sheet1'][5],
    'Ranked7': existing_data['Sheet1'][6], 'Reference': existing_data['Sheet1'][7],
    'Ranked8': existing_data['Sheet2'][0], 'Ranked9': existing_data['Sheet2'][1],
    'Ranked10': existing_data['Sheet2'][2], 'Ranked11': existing_data['Sheet2'][3]
}

# Calcul de la moyenne de référence et des variabilités existantes
reference_mean = calculate_reference_mean(existing_datasets['Reference'])
existing_variabilities = calculate_variabilities(existing_datasets, reference_mean)

# Taux de tolérance
tolerance = 0.1 * np.mean(list(existing_variabilities.values()))

# Ajout des nouvelles données
new_variabilities = calculate_variabilities(new_dataset, reference_mean)
all_variabilities = {**existing_variabilities, **new_variabilities}

# Regroupement des données
all_groups = group_datasets_by_variability(all_variabilities, tolerance)

# Trouver le groupe contenant les nouvelles données
for group_variability, labels in all_groups.items():
    if 'NewRanked' in labels:
        new_data_group = (group_variability, labels)
        break

# Affichage des résultats sans graphiques
print(f"Le nouveau jeu de données appartient au groupe avec une variabilité ~ {group_variability:.2f}")
print(f"Groupes : {all_groups}")
