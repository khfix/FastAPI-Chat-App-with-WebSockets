from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import chat, dependencies, user, websocket
from app.config import ALGORITHM, SECRET_KEY
from app.database import create_tables

print("Calling create_tables...")
create_tables()
print("create_tables called.")

app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(websocket.router)
app.include_router(chat.router, dependencies=[Depends(dependencies.get_db)])
app.include_router(user.router, dependencies=[Depends(dependencies.get_db)])

"""
This is the main module of the backend_chat application.
It sets up the FastAPI application, includes routers for chat, user, and websocket,
and adds middleware for CORS (Cross-Origin Resource Sharing).
The create_tables function is called to create the necessary database tables.
"""
