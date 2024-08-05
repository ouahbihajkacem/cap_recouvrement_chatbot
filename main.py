from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import cap_chatbot
from data_loader import debtor_data

app = FastAPI()

class Message(BaseModel):
    first_name: str
    last_name: str
    message: str

@app.post("/api/chat")
async def chat(message: Message):
    response = cap_chatbot.get_response(message.message, message.first_name, message.last_name, debtor_data)
    return {"response": response}
