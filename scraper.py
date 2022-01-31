import time
import requests
import json
import pandas as pd
import urllib

import config as cfg
import utils


ACCESS_ENDPOINT = "https://www.reddit.com/api/v1/access_token"
OAUTH_ENDPOINT = "https://oauth.reddit.com"
SUBREDDITS=[
    "wallstreetbets",
    "nfl",
    "buffalobills",
    "49ers"
]
POST_LIMIT = 10
POST_COLUMNS = ["id", "subreddit", "title", "created", "ups", "author", "selftext"]
COMMENT_LIMIT = 10
COMMENT_COLUMNS = ["id", "subreddit", "body", "created", "ups", "author", "stickied"]


class RedditScraper:
    client_id: str
    client_secret: str
    user_agent: str
    debug: bool
    dump_json: bool
    auth: dict
    auth_expiration: int
    auth_headers: dict[str, str]
    rate_limit: dict[str, str]

    def __init__(
        self, 
        client_id: str, 
        client_secret: str,
        user_agent: str,
        debug=False,
        dump_json=False
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.debug = debug
        self.dump_json = dump_json
        self.authenticate()


    def authenticate(self):
        headers = { "User-Agent": self.user_agent }

        # OAUTH
        response = requests.post(
            ACCESS_ENDPOINT,
            data = {"grant_type":"client_credentials"},
            auth = (self.client_id, self.client_secret),
            headers=headers
        )
        self.update_rate_limit(response)
        
        self.auth = response.json()
        self.auth_expiration = time.time() + self.auth["expires_in"]
        access_token = self.auth["access_token"]
        self.auth_headers = {**headers, **{"Authorization": f"Bearer {access_token}"}}


    def get_json(self, url: str, params: dict):
        if self.debug:
            print(f"Fetching {utils.encoded_url(url, params)}")

        # Check and refresh auth, if needed
        if self.auth_expiration <= time.time():
            if self.debug:
                print("Reauthenticating...")
            self.authenticate()

        # Check and wait for rate_limit, if needed
        if self.rate_limit["remaining"] == 0:
            reset = self.rate_limit["reset"]
            if self.debug:
                print(f"Rate limit reached. Waiting {reset} seconds...")
            time.sleep(reset)

        api_response = requests.get(
            url,
            headers=self.auth_headers,
            params=params
        )
        self.update_rate_limit(api_response)
        
        api_response_data = api_response.json()

        if self.dump_json:
            with open(f"{api_response.url}.json", "w") as outfile:
                json.dump(api_response_data, outfile, indent=4)
        
        return api_response_data


    def update_rate_limit(self, response: requests.Response):
        self.rate_limit = {
            "used": int(response.headers["X-Ratelimit-Used"]),
            "remaining": int(response.headers["X-Ratelimit-Remaining"]),
            "reset": int(response.headers["X-Ratelimit-Reset"]),
        }
        if self.debug:
            self.print_rate_limit()


    def print_rate_limit(self):
        used = self.rate_limit["used"]
        remaining = self.rate_limit["remaining"]
        reset = self.rate_limit["reset"]
        print(f"Used {used} | {remaining} remaining. Rate limit resets in {reset} seconds.")


    def get_posts(self, subreddit: str, sort = "top", limit = 10):
        endpoint = f"{OAUTH_ENDPOINT}/r/{subreddit}/{sort}/.json"
        params = {"limit": limit}
        api_response_data = self.get_json(endpoint, params)

        posts = api_response_data["data"]["children"]
        data = []
        for post in posts:
            post_kind = post["kind"]
            post_data = post["data"]
            values = [post_data[column] for column in POST_COLUMNS]
            data.append([post_kind, *values])

        df = pd.DataFrame(data, columns=["kind", *POST_COLUMNS])
        return df


    def get_post_comments(self, subreddit: str, post_id: str, sort = "top", limit = 10):
        endpoint = f"{OAUTH_ENDPOINT}/r/{subreddit}/comments/{post_id}/.json"
        params = {
            "sort": {sort},
            "limit": limit,
            "showmore": False
        }
        api_response_data = self.get_json(endpoint, params)

        # post = api_response_data[0]
        comments_obj = api_response_data[1] # is there a cleaner way to get this?
        comments = comments_obj["data"]["children"]
        data = []
        for comment in comments:
            comment_kind = comment["kind"]
            comment_data = comment["data"]
            values = [comment_data[column] for column in COMMENT_COLUMNS]
            data.append([post_id, comment_kind, *values])

        df = pd.DataFrame(data, columns=["post_id", "kind", *COMMENT_COLUMNS])
        return df


def main():
    user_agent = f"script:{cfg.NAME}:{cfg.VERSION} (by /u/{cfg.REDDIT_USERNAME})" # <platform>:<app ID>:<version string> (by /u/<reddit username>)
    scraper = RedditScraper(
        client_id=cfg.CLIENT_ID, 
        client_secret = cfg.CLIENT_SECRET,
        user_agent = user_agent,
        debug = cfg.DEBUG,
        dump_json = cfg.DUMP_JSON
    )
    
    # TODO: Check out live threads: https://www.reddit.com/dev/api/#section_live

    # Uncomment to run indefinitely
    # while True:
    for subreddit in SUBREDDITS:
        top_posts_df = scraper.get_posts(subreddit, sort="top", limit=POST_LIMIT)
        if not top_posts_df.empty:
            top_comments_dfs = []
            for _, row in top_posts_df.iterrows():
                top_comments_df = scraper.get_post_comments(subreddit, row["id"], sort="top", limit=COMMENT_LIMIT)
                top_comments_dfs.append(top_comments_df)
            
            all_top_comments_df = pd.concat(top_comments_dfs, sort=False)


if __name__ == "__main__":
    main()