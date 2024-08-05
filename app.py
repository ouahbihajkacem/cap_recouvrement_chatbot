import streamlit as st
from data_loader import debtor_data
from chatbot import cap_chatbot

st.title("CAP Recouvrement Chatbot")

# Initialiser les variables de session
if 'user_verified' not in st.session_state:
    st.session_state['user_verified'] = False
    st.session_state['first_name'] = ""
    st.session_state['last_name'] = ""
    st.session_state['qa_history'] = []  # Pour stocker l'historique des questions-réponses

# Afficher les champs de saisie pour le prénom et le nom si l'utilisateur n'est pas vérifié
if not st.session_state['user_verified']:
    first_name = st.text_input("Entrez votre prénom").strip().lower()
    last_name = st.text_input("Entrez votre nom").strip().lower()

    if st.button("Se Connecter"):
        if first_name and last_name:
            debtor_data['prenom_debiteur'] = debtor_data['prenom_debiteur'].str.strip().str.lower()
            debtor_data['nom_debiteur'] = debtor_data['nom_debiteur'].str.strip().str.lower()
            user = debtor_data[(debtor_data['prenom_debiteur'] == first_name) & (debtor_data['nom_debiteur'] == last_name)]
            if not user.empty:
                st.session_state['user_verified'] = True
                st.session_state['first_name'] = first_name
                st.session_state['last_name'] = last_name
                st.success(f"Bonjour {first_name.capitalize()} {last_name.capitalize()}, vous pouvez maintenant poser votre question.")
            else:
                st.error("Débiteur non trouvé dans la base de données de CAP Recouvrement! Veuillez réessayer.")

# Si l'utilisateur est vérifié, afficher le champ de saisie pour la question
if st.session_state['user_verified']:
    first_name = st.session_state['first_name']
    last_name = st.session_state['last_name']
    
    user_input = st.text_input("Posez votre question")
    
    if st.button("Envoyer") and user_input:
        response = cap_chatbot.get_response(user_input, first_name, last_name, debtor_data)
        # Ajouter la question et la réponse à l'historique
        st.session_state['qa_history'].append((user_input, response))
    
    # Afficher l'historique des questions-réponses
    for question, answer in st.session_state['qa_history']:
        st.markdown(f"""
        <div style='background-color: #e8f4f8; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
            <p style='margin: 0; color: #333;'><strong>Question :</strong> {question}</p>
            <p style='margin: 0; color: #333;'><strong>Réponse :</strong> {answer}</p>
        </div>
        """, unsafe_allow_html=True)

    if user_input.lower() in ["au revoir", "bonne soirée"]:
        st.session_state['user_verified'] = False
        st.session_state['first_name'] = ""
        st.session_state['last_name'] = ""
        st.session_state['qa_history'] = []  # Réinitialiser l'historique
        st.write("Au revoir ! Passez une bonne journée !")
