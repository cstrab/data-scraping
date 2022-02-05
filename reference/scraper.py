import time
import requests
import json
import pandas as pd
import praw

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
            with open(f"{api_response.url.replace('/', '|')}.json", "w") as outfile:
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
        posts_df = self.parse_posts(api_response_data)
        return posts_df


    def parse_posts(self, response_json: dict):
        posts = response_json["data"]["children"]
        data = []
        for post in posts:
            post_kind = post["kind"]
            post_data = post["data"]
            values = [post_data[column] for column in POST_COLUMNS]
            data.append([post_kind, *values])

        df = pd.DataFrame(data, columns=["kind", *POST_COLUMNS])
        return df


    # Follows a subreddit by polling for new posts. Saves posts to data store.
    def follow_subreddit(self, subreddit: str, limit = 100, pollrate = 5):
        endpoint = f"{OAUTH_ENDPOINT}/r/{subreddit}/new/.json"
        params = {"limit": limit}
        while True:
            api_response_data = self.get_json(endpoint, params)
            posts_df = self.parse_posts(api_response_data)
            if not posts_df.empty:
                self.save_posts(posts_df)
                last_post = posts_df.iloc[0]
                before = f"{last_post['kind']}_{last_post['id']}"
                params["before"] = before
            else:
                print(f"No new posts in {subreddit}. Waiting {pollrate} seconds...")
                time.sleep(pollrate)


    def save_posts(self, posts_df: pd.DataFrame):
        # TODO: Save posts to a db
        print("Saving posts...")
        print(posts_df)


    def follow_subreddit_hot(self, subreddit: str, limit = 10, pollrate = 5):
        endpoint = f"{OAUTH_ENDPOINT}/r/{subreddit}/hot/.json"
        params = {"limit": limit}
        posts_df: pd.DataFrame = pd.DataFrame()
        comment_tails = {}
        while True:
            # TODO: Refactor the next 10 lines
            api_response_data = self.get_json(endpoint, params)
            new_posts_df = self.parse_posts(api_response_data)
            if not new_posts_df.empty:
                self.save_posts(new_posts_df)
                last_post = new_posts_df.iloc[0]
                before = f"{last_post['kind']}_{last_post['id']}"
                params["before"] = before
            else:
                print(f"No new hot posts in {subreddit}. Waiting {pollrate} seconds...")
                time.sleep(pollrate)

            posts_df = pd.concat([new_posts_df, posts_df], sort=False).head(10)
            comment_heads = {}
            for _, post in posts_df.iterrows():
                post_id = post['id']
                if post_id in comment_tails:
                    comment_heads[post_id] = comment_tails[post_id]
                else:
                    print(f"New hot post {post_id} in {subreddit}.")
                    comment_heads[post_id] = ""
            
            # TODO: Need to figure out how to get new comments only, seems 'before' is not a thing here??
            # for post_id, before in comment_heads.items():
            #     while True:
            #         # Get comments and store the before value
            #         comments_df = self.get_post_comments(subreddit, post_id, sort="new", limit=100)
            #         if not comments_df.empty:
            #             self.save_comments(comments_df)
            #             last_comment = comments_df.iloc[0]
            #             before = f"{last_comment['kind']}_{last_comment['id']}"
            #             comment_heads[post_id] = before
            #         else:
            #             print(f"No new comments in {subreddit} post {post_id}.")
            #             break

            comment_tails = comment_heads


    def save_comments(self, comments_df: pd.DataFrame):
        # TODO: Save comments to a db
        print("Saving comments...")
        print(comments_df)


    # TODO: May need to return more than just a df of comments (before, after, etc.)
    def get_post_comments(self, subreddit: str, post_id: str, sort = "top", limit = 10):
        endpoint = f"{OAUTH_ENDPOINT}/r/{subreddit}/comments/{post_id}/.json"
        params = {
            "sort": {sort},
            "limit": limit,
            "showmore": False
        }

        api_response_data = self.get_json(endpoint, params)
        comments_df = self.parse_comments(api_response_data)
        comments_df['post_id'] = post_id
        return comments_df
        
    
    def parse_comments(self, response_json: dict):
        comments_obj = response_json[1] # is there a cleaner way to get this?
        comments = comments_obj["data"]["children"]
        data = []
        for comment in comments:
            comment_kind = comment["kind"]
            comment_data = comment["data"]
            values = [comment_data[column] for column in COMMENT_COLUMNS]
            data.append([comment_kind, *values])

        df = pd.DataFrame(data, columns=["kind", *COMMENT_COLUMNS])
        return df


def main():
    user_agent = f"script:{cfg.NAME}:{cfg.VERSION} (by /u/{cfg.REDDIT_USERNAME})" # <platform>:<app ID>:<version string> (by /u/<reddit username>)
    reddit = praw.Reddit(
        client_id=cfg.CLIENT_ID, 
        client_secret = cfg.CLIENT_SECRET,
        user_agent = user_agent,
    )
    
    top_posts = reddit.subreddit(SUBREDDITS[0]).top(limit=POST_LIMIT)
    print(top_posts)


if __name__ == "__main__":
    main()