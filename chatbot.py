from transformers import AutoTokenizer, TFAutoModel
import pandas as pd
import numpy as np
import tensorflow as tf
from data_loader import debtor_data
from indexer import vector_db, metadata

# Charger le modèle de transformers
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = TFAutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

def verify_user(first_name, last_name, debtor_data):
    user = debtor_data[(debtor_data['prenom_debiteur'] == first_name) & (debtor_data['nom_debiteur'] == last_name)]
    return user if not user.empty else None

class CAPRecouvrementChatBot:
    def __init__(self, vector_db, metadata):
        self.vector_db = vector_db
        self.metadata = metadata
        self.memory = {}

    def get_response(self, user_input, first_name, last_name, debtor_data):
        user = verify_user(first_name, last_name, debtor_data)
        if user is not None:
            user_key = f"{first_name}_{last_name}"
            self.memory[user_key] = user.to_dict('records')[0]
            response_template = self.find_response_template(user_input)
            if response_template:
                response = self.fill_template(response_template, self.memory[user_key], user_input)
                return response.encode('utf-8').decode()  # Assurez-vous que la réponse est en UTF-8
            else:
                return "Désolé, je ne suis pas en mesure de trouver une réponse appropriée."
        else:
            return "Je ne trouve pas vos informations dans notre base de données."

    def find_response_template(self, prompt):
        inputs = tokenizer(prompt, return_tensors="tf")
        outputs = model(**inputs)
        user_input_embedding = outputs.last_hidden_state[:, 0, :].numpy().reshape(1, -1)  # Reshape pour correspondre à la forme attendue
        D, I = self.vector_db.search(user_input_embedding, k=1)
        if I[0][0] != -1:
            response_template = self.metadata[I[0][0]]['response']
            return response_template
        else:
            return None
    
    def fill_template(self, template, user, user_input):
        response = template

        if any(keyword in user_input.lower() for keyword in ["téléphone", "phone", "numéro de téléphone", "phone number", "contact my account manager", "contacter mon gestionnaire"]):
            response = "Le numéro de téléphone de votre gestionnaire de compte est {telephone_gestionnaire_amiable}.".format(
               telephone_gestionnaire_amiable=user['telephone_gestionnaire_amiable'])
        elif any(keyword in user_input.lower() for keyword in ["gestionnaire", "responsable", "responsable du dossier", "qui est mon gestionnaire", "dossier"]):
            response = "Votre gestionnaire de dossier est {prenom_gestionnaire_amiable} {nom_gestionnaire_amiable}. Vous pouvez le joindre au {telephone_gestionnaire_amiable}.".format(
              prenom_gestionnaire_amiable=user['prenom_gestionnaire_amiable'],
              nom_gestionnaire_amiable=user['nom_gestionnaire_amiable'], 
              telephone_gestionnaire_amiable=user['telephone_gestionnaire_amiable'])
        elif any(keyword in user_input.lower() for keyword in ["account manager", "corporate account", "manager", "call to pay"]):
            response = "Your account manager is {prenom_gestionnaire_amiable} {nom_gestionnaire_amiable}. You can reach him by calling {telephone_gestionnaire_amiable}.".format(
            prenom_gestionnaire_amiable=user['prenom_gestionnaire_amiable'],
            nom_gestionnaire_amiable=user['nom_gestionnaire_amiable'],
            telephone_gestionnaire_amiable=user['telephone_gestionnaire_amiable'])
        elif any(keyword in user_input.lower() for keyword in ["argent", "somme", "payer", "demande", "dette"]):
            response = response.replace(',,,,,', str(user['decompte_total_solde']), 1)
            response = response.replace(',,,,,', user['raison_sociale_client'], 1)
        elif any(keyword in user_input.lower() for keyword in ["money", "amount", "sums", "pay", "request"]):
            response = response.replace(',,,,,', user['raison_sociale_client'], 1)
            response = response.replace(',,,,,', str(user['decompte_total_solde']), 1)
        elif any(keyword in user_input.lower() for keyword in ["créancier", "créditeur", "creancier", "crediteur", "salle de sport", "salle", "creditor", "gym"]):
            response = response.replace('Mettre le nom commercial du client orange bleue', user['raison_sociale_client'])
        elif any(keyword in user_input.lower() for keyword in ["au revoir", "bonne soirée"]):
            response = "Au revoir ! Passez une bonne journée !"
        return response

# Initialiser le chatbot
cap_chatbot = CAPRecouvrementChatBot(vector_db, metadata)
