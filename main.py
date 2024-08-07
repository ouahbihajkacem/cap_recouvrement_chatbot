import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
from uuid import uuid4
from chatbot import cap_chatbot
from data_loader import debtor_data

# Configure logs
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Add CORS Middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session management
sessions: Dict[str, Dict] = {}

class Message(BaseModel):
    first_name: str
    last_name: str
    message: str
    session_id: Optional[str] = None

class UserVerification(BaseModel):
    first_name: str
    last_name: str

def get_session(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = {"history": [], "user_verified": False, "first_name": "", "last_name": ""}
    return sessions[session_id]

@app.post("/api/verify_user")
async def verify_user(user: UserVerification):
    logging.info(f"Received verification request: {user}")
    first_name = user.first_name.strip().lower()
    last_name = user.last_name.strip().lower()
    user_data = debtor_data[(debtor_data['prenom_debiteur'].str.lower() == first_name) & (debtor_data['nom_debiteur'].str.lower() == last_name)]
    if not user_data.empty:
        logging.info(f"User found: {user_data}")
        session_id = str(uuid4())
        session = get_session(session_id)
        session["user_verified"] = True
        session["first_name"] = first_name
        session["last_name"] = last_name
        return {"found": True, "session_id": session_id}
    else:
        logging.warning("User not found.")
        return {"found": False}

@app.post("/api/chat")
async def chat(message: Message):
    logging.info(f"Received chat message: first_name='{message.first_name}' last_name='{message.last_name}' message='{message.message}' session_id='{message.session_id}'")
    if message.session_id and message.session_id in sessions:
        session = get_session(message.session_id)
        if session["user_verified"]:
            first_name = session["first_name"]
            last_name = session["last_name"]
            user = debtor_data[(debtor_data['prenom_debiteur'].str.lower() == first_name) & (debtor_data['nom_debiteur'].str.lower() == last_name)]
            if not user.empty:
                logging.info(f"User found for chat: {user}")
                response = cap_chatbot.get_response(message.message, first_name, last_name, debtor_data)
                session["history"].append({"user": message.message, "bot": response})
                logging.info(f"Chat response: {response}")
                return {"response": response, "session_id": message.session_id}
            else:
                logging.warning("User not found in database during chat.")
                return {"response": "Je ne trouve pas vos informations dans notre base de données.", "session_id": message.session_id}
        else:
            logging.warning("User not verified in session.")
            return {"response": "Utilisateur non vérifié.", "session_id": message.session_id}
    else:
        logging.warning("Invalid session or session not found.")
        return {"response": "Session invalide ou utilisateur non vérifié.", "session_id": str(uuid4())}

@app.post("/api/log_interaction")
async def log_interaction(interaction: dict):
    # Log interaction in a file or database
    with open("interactions_log.txt", "a") as log_file:
        log_file.write(f"{interaction}\n")
    logging.info(f"Logged interaction: {interaction}")
    return {"status": "success"}
