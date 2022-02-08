import os
from dotenv import load_dotenv


load_dotenv() # Loads variables from .env file into environment

DEBUG=False
DATABASE_HOST=os.environ.get("DATABASE_HOST")
DATABASE_PORT=os.environ.get("DATABASE_PORT")
DATABASE_NAME=os.environ.get("DATABASE_NAME")
DATABASE_USER=os.environ.get("DATABASE_USER")
DATABASE_PASSWORD=os.environ.get("DATABASE_PASSWORD")