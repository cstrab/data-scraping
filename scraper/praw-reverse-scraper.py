import time
import config as cfg

# See ./classes/reddit_scraper.py for class definition
from classes.reddit_scraper import RedditScraper


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
    scraper.get_before_time()

    while True:
        try:
            num_scraped = scraper.reverse_scrape_comments()
            if num_scraped == 0:
                print("No more comments scraped, stopping...")
                break
        except Exception as exp:
            # Usually caused by 503 from Reddit api
            print(f"Error scraping comments: {exp}")
            print(f"Retrying in {cfg.RETRY_SECONDS} seconds...")
            time.sleep(cfg.RETRY_SECONDS)


if __name__ == "__main__":
    main()
