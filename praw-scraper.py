import praw
from multiprocessing import Process

import config as cfg


SUBREDDIT = "wallstreetbets"
POST_LIMIT = 10


def stream_submissions(subreddit: praw.reddit.Subreddit):
    for submission in subreddit.stream.submissions():
        print("--- SUBMISSION ---")
        print(submission.title)


def stream_comments(subreddit: praw.reddit.Subreddit):
    for comment in subreddit.stream.comments():
        # Get comment submission
        # Check if submission is in DB
        # If not, save submission
        # Save comment with fk to submission
        print(comment.body)


def main():
    user_agent = f"script:{cfg.NAME}:{cfg.VERSION} (by /u/{cfg.REDDIT_USERNAME})" # <platform>:<app ID>:<version string> (by /u/<reddit username>)
    reddit = praw.Reddit(
        client_id=cfg.CLIENT_ID, 
        client_secret = cfg.CLIENT_SECRET,
        user_agent = user_agent,
    )
    subreddit = reddit.subreddit(SUBREDDIT)
    # Don't need to necessarily stream all submissions, but rather
    # retrieve them based on the comment stream, as needed
    stream_comments(subreddit)
    # Process(target=stream_submissions, args=(subreddit,)).start()
    # Process(target=stream_comments, args=(subreddit,)).start()    


if __name__ == "__main__":
    main()
