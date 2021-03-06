from typing import Dict
import praw
import psaw
import psycopg2
from pandas_datareader import data as pdr
import nlp


class RedditScraper:

    reddit: praw.reddit.Reddit
    subreddit: praw.reddit.Subreddit
    psapi: psaw.PushshiftAPI
    db_conn: dict
    debug: bool
    symbols = []
    before_time = 0

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
        
        # pushshift api for historical scraping
        self.psapi = psaw.PushshiftAPI(self.reddit)

        if database_host:
            self.db_conn = {
                "database": database_name,
                "user": database_user,
                "password": database_password,
                "host": database_host,
                "port": database_port
            }
            self.check_db_connection()
        else:
            print("No database config provided. Results will not be saved.")

        self.debug = debug


    def get_db_connection(self):
        return psycopg2.connect(**self.db_conn)


    def check_db_connection(self):
        try:
            with self.get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    print(f"Connected to {self.db_conn['database']} as {self.db_conn['user']}.")
        except Exception as exp:
            print(f"Failed to connect to {self.db_conn['database']}: {exp}")


    def get_symbols(self):
        if self.debug:
            print("Getting symbols...")

        if not self.db_conn:
            return self.fetch_symbols()
        
        with self.get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = """SELECT symbol FROM symbols
                    WHERE listing_exchange IN ('Q', 'N');"""
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    symbols = {result[0]: True for result in results}
                    self.symbols = symbols
                except Exception as exp:
                    print(f"Error getting symbols: {exp}")
    

    def fetch_symbols(self):
        symbols = pdr.get_nasdaq_symbols()
        self.symbols = {symbol: True for symbol, _ in symbols.iterrows()}


    def submission_exists(self, submission: praw.reddit.Submission) -> bool:
        if not self.db_conn:
            return False

        with self.get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = "SELECT 1 FROM submissions WHERE id = %s;"
                    cursor.execute(sql, (submission.id,))
                    result = cursor.fetchone()
                    exists = result is not None
                    return exists
                except Exception as exp:
                    print(f"Error checking for submission {submission.id}: {exp}")
                    return False


    def save_submission(self, submission: praw.reddit.Submission) -> None:
        if self.debug:
            print(f"Saving submission {submission.id}...")

        if not self.db_conn:
            return False
            
        with self.get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = """INSERT INTO submissions (id, title, author, created) 
                    VALUES (%s, %s, %s, %s);"""
                    cursor.execute(sql, (
                        submission.id,
                        submission.title,
                        submission.author.name if submission.author else "",
                        int(submission.created),
                    ))
                    connection.commit()
                except Exception as exp:
                    connection.rollback()
                    print(f"Error saving submission {submission.id}: {exp}")
   

    def comment_exists(self, comment: praw.reddit.Comment) -> bool:
        if not self.db_conn:
            return False

        with self.get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = "SELECT 1 FROM comments WHERE id = %s;"
                    cursor.execute(sql, (comment.id,))
                    result = cursor.fetchone()
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
        if not self.db_conn:
            return
        
        with self.get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = """INSERT INTO comments (id, submission_id, body, author, created) 
                    VALUES (%s, %s, %s, %s, %s);"""
                    cursor.execute(sql, (
                        comment.id,
                        comment.submission.id,
                        comment.body,
                        comment.author.name if comment.author else "",
                        int(comment.created),
                    ))
                    connection.commit()
                except Exception as exp:
                    connection.rollback()
                    print(f"Error inserting comment {comment.id}: {exp}")

        
    def analyze_comment(self, comment: praw.reddit.Comment):
        sentiments = self.get_sentiments(comment)
        if self.debug:
            for symbol in sentiments:
                print(f"{symbol} mentioned in {comment.id} with sentiment {sentiments[symbol]['sentiment']}.")
        
        if not self.db_conn:
            return
        
        with self.get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = """INSERT INTO mentions (symbol, comment_id, sentiment) 
                    VALUES (%s, %s, %s);"""
                    for symbol in sentiments:
                        cursor.execute(sql, (
                            symbol,
                            comment.id,
                            sentiments[symbol]["sentiment"],
                        ))
                    connection.commit()
                except Exception as exp:
                    connection.rollback()
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

    
    def reverse_scrape_comments(self) -> int:
        print(f"Scraping all comments from {self.subreddit} before {self.before_time}...")
        num_scraped = 0 # Keep track of number scraped to determine if done
        params = {
            "subreddit": self.subreddit.display_name,
            "before": self.before_time + 1 # NOTE: Might be needed to avoid gaps?
        }
        for comment in self.psapi.search_comments(**params):
            # Check if comment submission is already in DB
            if not self.submission_exists(comment.submission):
                # If not, save submission
                self.save_submission(comment.submission)
            # Check if comment is already in DB
            elif self.debug:
                print(f"Already saved submission {comment.submission.id}")
            if not self.comment_exists(comment):
                # If not, save comment with fk to submission
                self.save_comment(comment)
                num_scraped += 1
            elif self.debug:
                print(f"Already saved comment {comment.id}")
            self.before_time = int(comment.created)

        return num_scraped


    def get_before_time(self) -> str:
        if not self.db_conn:
            return False

        with self.get_db_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = """SELECT created FROM comments
                    ORDER BY created
                    LIMIT 1"""
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    self.before_time = result[0]
                except Exception as exp:
                    print(f"Error getting oldest comment time: {exp}")
