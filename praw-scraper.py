import praw
import psycopg2

import config as cfg


# DB
conn = psycopg2.connect(
    database=cfg.DATABASE_NAME,
    user=cfg.DATABASE_USER,
    password=cfg.DATABASE_PASSWORD,
    host=cfg.DATABASE_HOST,
    port=cfg.DATABASE_PORT
)
cur = conn.cursor()


def submission_exists(submission: praw.reddit.Submission) -> bool:
    try:
        sql = "SELECT 1 FROM submissions WHERE id = %s;"
        cur.execute(sql, (submission.id,))
        result = cur.fetchone()
        exists = result is not None
        return exists
    except Exception as exp:
        print(f"Error checking for submission {submission.id}: {exp}")
        return False


def save_submission(submission: praw.reddit.Submission) -> None:
    if cfg.DEBUG:
        print(f"Saving submission {submission.id}...")
        
    try:
        sql = """INSERT INTO submissions (id, title, author, created) 
        VALUES (%s, %s, %s, %s);"""
        cur.execute(sql, (
            submission.id,
            submission.title,
            submission.author.name,
            int(submission.created),
        ))
        conn.commit()
    except Exception as exp:
        conn.rollback()
        print(f"Error saving submission {submission.id}: {exp}")


def save_comment(comment: praw.reddit.Comment) -> None:
    if cfg.DEBUG:
        print(f"Saving comment on submission {comment.submission.id}...")
    
    try:
        sql = """INSERT INTO comments (id, submission_id, body, author, created) 
        VALUES (%s, %s, %s, %s, %s);"""
        cur.execute(sql, (
            comment.id,
            comment.submission.id,
            comment.body,
            comment.author.name,
            int(comment.created),
        ))
        conn.commit()
    except Exception as exp:
        conn.rollback()
        print(f"Error saving comment {comment.id}: {exp}")


def stream_comments(subreddit: praw.reddit.Subreddit) -> None:
    for comment in subreddit.stream.comments():
        # Check if comment submission is in DB
        if not submission_exists(comment.submission):
            # If not, save submission
            save_submission(comment.submission)
        # Save comment with fk to submission
        save_comment(comment)


def main() -> None:
    user_agent = f"script:{cfg.NAME}:{cfg.VERSION} (by /u/{cfg.REDDIT_USERNAME})" # <platform>:<app ID>:<version string> (by /u/<reddit username>)
    reddit = praw.Reddit(
        client_id=cfg.CLIENT_ID, 
        client_secret = cfg.CLIENT_SECRET,
        user_agent = user_agent,
    )
    subreddit = reddit.subreddit(cfg.SUBREDDIT)
    stream_comments(subreddit)


if __name__ == "__main__":
    main()
