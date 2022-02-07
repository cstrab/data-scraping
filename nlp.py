from typing import Text
from textblob import TextBlob


def get_words(text: str):
    blob = TextBlob(text)
    return blob.words


def get_nouns(text: str):
    blob = TextBlob(text)
    return blob.noun_phrases


def get_sentences(text: str):
    blob = TextBlob(text)
    return blob.sentences


def get_sentiment(text: str):
    blob = TextBlob(text)
    return blob.sentiment
