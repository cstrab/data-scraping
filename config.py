import os
from dotenv import load_dotenv


load_dotenv() # Loads variables from .env file into environment

NAME="big.data.boys"
REDDIT_USERNAME="cheeebz"
VERSION="0.0.1"
CLIENT_ID="QpA5EiFQsqYoj2nbkqrObQ"
CLIENT_SECRET=os.environ.get("CLIENT_SECRET")