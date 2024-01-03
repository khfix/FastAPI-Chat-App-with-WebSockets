from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import chat, dependencies, user, websocket
from app.config import ALGORITHM, SECRET_KEY
from app.database import create_tables  # Import create_tables

print("Calling create_tables...")
create_tables()
print("create_tables called.")

app = FastAPI()


# CORS setup
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

# Include routers
app.include_router(websocket.router)
app.include_router(chat.router, dependencies=[Depends(dependencies.get_db)])
app.include_router(user.router, dependencies=[Depends(dependencies.get_db)])

# Call create_tables to create the database tables
