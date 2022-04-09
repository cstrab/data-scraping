import os
from dotenv import load_dotenv


load_dotenv() # Loads variables from .env file into environment

DEBUG=False
NAME="big.data.boys"
VERSION="0.0.1"
REDDIT_USERNAME=os.environ.get("REDDIT_USERNAME") or "cheeebz"
CLIENT_ID=os.environ.get("CLIENT_ID") or "i7jkVr6-TGnrQVdZ7WHgIQ"
CLIENT_SECRET=os.environ.get("CLIENT_SECRET")
SUBREDDIT=os.environ.get("SUBREDDIT") or "wallstreetbets"
RETRY_SECONDS=os.environ.get("RETRY_SECONDS") or 30

DATABASE_HOST=os.environ.get("DATABASE_HOST")
DATABASE_PORT=os.environ.get("DATABASE_PORT")
DATABASE_NAME=os.environ.get("DATABASE_NAME")
DATABASE_USER=os.environ.get("DATABASE_USER")
DATABASE_PASSWORD=os.environ.get("DATABASE_PASSWORD")