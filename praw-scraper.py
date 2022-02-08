import praw
import psycopg2
import time
from pandas_datareader import data as pdr

import config as cfg
import nlp


class RedditScraper:

    reddit: praw.reddit.Reddit
    subreddit: praw.reddit.Subreddit
    connection = None
    cursor = None
    debug: bool
    symbols = []

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        subreddit: str,
        debug = False,
        database_host = "",
        database_port = 5432,
        database_name = "",
        database_user = "",
        database_password = "",
    ):
        self.reddit = praw.Reddit(
            client_id=client_id, 
            client_secret = client_secret,
            user_agent = user_agent,
        )
        self.subreddit = self.reddit.subreddit(subreddit)

        if database_host:
            self.connection = psycopg2.connect(
                database=database_name,
                user=database_user,
                password=database_password,
                host=database_host,
                port=database_port
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to {database_name} as {database_user}.")
        else:
            print("No database config provided. Results will not be saved.")

        self.debug = debug


    def get_symbols(self):
        if self.debug:
            print("Getting symbols...")

        if not self.connection:
            return self.fetch_symbols()
        
        try:
            sql = """SELECT symbol FROM symbols
            WHERE listing_exchange IN ('Q', 'N');"""
            # sql = """SELECT * FROM public.symbols WHERE LENGTH(symbol) > 2
            # AND listing_exchange IN ('Q', 'N')"""
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            symbols = {result[0]: True for result in results}
            self.symbols = symbols
        except Exception as exp:
            print(f"Error getting symbols: {exp}")
    

    def fetch_symbols(self):
        symbols = pdr.get_nasdaq_symbols()
        self.symbols = {symbol: True for symbol, _ in symbols.iterrows()}


    def submission_exists(self, submission: praw.reddit.Submission) -> bool:
        if not self.connection:
            return False

        try:
            sql = "SELECT 1 FROM submissions WHERE id = %s;"
            self.cursor.execute(sql, (submission.id,))
            result = self.cursor.fetchone()
            exists = result is not None
            return exists
        except Exception as exp:
            print(f"Error checking for submission {submission.id}: {exp}")
            return False


    def save_submission(self, submission: praw.reddit.Submission) -> None:
        if self.debug:
            print(f"Saving submission {submission.id}...")

        if not self.connection:
            return False
            
        try:
            sql = """INSERT INTO submissions (id, title, author, created) 
            VALUES (%s, %s, %s, %s);"""
            self.cursor.execute(sql, (
                submission.id,
                submission.title,
                submission.author.name if submission.author else "",
                int(submission.created),
            ))
            self.connection.commit()
        except Exception as exp:
            self.connection.rollback()
            print(f"Error saving submission {submission.id}: {exp}")
   

    def comment_exists(self, comment: praw.reddit.Comment) -> bool:
        if not self.connection:
            return False

        try:
            sql = "SELECT 1 FROM comments WHERE id = %s;"
            self.cursor.execute(sql, (comment.id,))
            result = self.cursor.fetchone()
            exists = result is not None
            return exists
        except Exception as exp:
            print(f"Error checking for comment {comment.id}: {exp}")
            return False


    def save_comment(self, comment: praw.reddit.Comment) -> None:
        if self.debug:
            print(f"Saving comment on submission {comment.submission.id}...")
       
        self.insert_comment(comment)
        self.analyze_comment(comment)


    def insert_comment(self, comment: praw.reddit.Comment) -> None:
        if not self.connection:
            return
        
        try:
            sql = """INSERT INTO comments (id, submission_id, body, author, created) 
            VALUES (%s, %s, %s, %s, %s);"""
            self.cursor.execute(sql, (
                comment.id,
                comment.submission.id,
                comment.body,
                comment.author.name if comment.author else "",
                int(comment.created),
            ))
            self.connection.commit()
        except Exception as exp:
            self.connection.rollback()
            print(f"Error inserting comment {comment.id}: {exp}")

        
    def analyze_comment(self, comment: praw.reddit.Comment):
        sentiments = self.get_sentiments(comment)
        if self.debug:
            for symbol in sentiments:
                print(f"{symbol} mentioned in {comment.id} with sentiment {sentiments[symbol]['sentiment']}.")
        
        if not self.connection:
            return
        
        try:
            sql = """INSERT INTO mentions (symbol, comment_id, sentiment) 
            VALUES (%s, %s, %s);"""
            for symbol in sentiments:
                self.cursor.execute(sql, (
                    symbol,
                    comment.id,
                    sentiments[symbol]["sentiment"],
                ))
            self.connection.commit()
        except Exception as exp:
            self.connection.rollback()
            print(f"Error inserting mentions for comment {comment.id}: {exp}") 


    def get_sentiments(self, comment: praw.reddit.Comment) -> dict:
        sentiments = {}
        sentences = nlp.get_sentences(comment.body)
        for sentence in sentences:
            for noun_phrase in sentence.noun_phrases:
                upper = noun_phrase.upper()
                if upper in self.symbols:
                    if upper not in sentiments:
                        sentiments[upper] = {
                            "mentions": 1,
                            "sentiment": sentence.sentiment.polarity
                        }
                    else:
                        sentiments[upper] = {
                            "mentions": sentiments[upper]["mentions"] + 1,
                            "sentiment": (sentiments[upper]["sentiment"] * sentiments[upper]["mentions"] + sentence.sentiment.polarity) / (sentiments[upper]["mentions"] + 1)
                        }
        return sentiments


    def stream_comments(self) -> None:
        print(f"Streaming comments from {self.subreddit}...")
        for comment in self.subreddit.stream.comments():
            # Check if comment submission is already in DB
            if not self.submission_exists(comment.submission):
                # If not, save submission
                self.save_submission(comment.submission)
            # Check if comment is already in DB
            if not self.comment_exists(comment):
                # If not, save comment with fk to submission
                self.save_comment(comment)


def main():
    user_agent = f"script:{cfg.NAME}:{cfg.VERSION} (by /u/{cfg.REDDIT_USERNAME})" # <platform>:<app ID>:<version string> (by /u/<reddit username>)
    print(f"Starting RedditScraper as {user_agent}.")
    scraper = RedditScraper(
        client_id = cfg.CLIENT_ID, 
        client_secret = cfg.CLIENT_SECRET,
        user_agent = user_agent,
        subreddit= cfg.SUBREDDIT,
        debug = cfg.DEBUG,
        database_host = cfg.DATABASE_HOST,
        database_port = cfg.DATABASE_PORT,
        database_name = cfg.DATABASE_NAME,
        database_user = cfg.DATABASE_USER,
        database_password = cfg.DATABASE_PASSWORD
    )
    scraper.get_symbols()

    while True:
        try:
            scraper.stream_comments()
        except Exception as exp:
            # Usually caused by 503 from Reddit api
            print(f"Error streaming comments: {exp}")
            print(f"Retrying in {cfg.RETRY_SECONDS} seconds...")
            time.sleep(cfg.RETRY_SECONDS)


if __name__ == "__main__":
    main()
