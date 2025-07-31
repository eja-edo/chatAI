from fastapi import FastAPI
from app.api.routes import users
from app.api.routes import chat_session


app = FastAPI()

app.include_router(users.router, prefix="/user")
app.include_router(chat_session.router, prefix="/chat-session")
