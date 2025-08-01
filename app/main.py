from fastapi import FastAPI
from app.api.routes import users
from app.api.routes import chat_session

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:5173",  
]

# Add CORS middleware here
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/user")
app.include_router(chat_session.router, prefix="/chat-session")

