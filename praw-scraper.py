import praw
import psycopg2
import time

import config as cfg


class RedditScraper:

    reddit: praw.reddit.Reddit
    subreddit: praw.reddit.Subreddit
    connection = None
    cursor = None
    debug: bool

    def __init__(
        self,
        client_id,
        client_secret,
        user_agent,
        subreddit,
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

        if not self.connection:
            return False
        
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
            print(f"Error saving comment {comment.id}: {exp}")


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


def main() -> None:
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

    while True:
        try:
            scraper.stream_comments()
        except Exception as exp:
            print(f"Error streaming comments: {exp}")
            print(f"Retrying in {cfg.RETRY_SECONDS} seconds...")
            time.sleep()


if __name__ == "__main__":
    main()
