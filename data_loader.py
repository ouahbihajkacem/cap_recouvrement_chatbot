import pandas as pd

def load_excel_data(file_path):
    data = pd.read_excel(file_path)
    print(data.head())  # Affiche les premières lignes des données pour vérification
    return data

def load_chatbot_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip().split('::') for line in file.readlines() if '::' in line]

# Charger les données
debtor_data = load_excel_data('data/Classeur.xlsx')
qa_pairs = load_chatbot_data('data/Data_Chatbot.txt')
