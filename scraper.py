import requests
import json
import pandas as pd

import config as cfg


ACCESS_ENDPOINT = "https://www.reddit.com/api/v1/access_token"
OAUTH_ENDPOINT = "https://oauth.reddit.com"
SUBREDDITS=[
    "wallstreetbets"
    # "nfl",
    # "buffalobills",
    # "49ers"
]
POST_LIMIT = 10
POST_COLUMNS = ["id", "subreddit", "title", "created", "ups", "author", "selftext"]
COMMENT_LIMIT = 10
COMMENT_COLUMNS = ["id", "subreddit", "body", "created", "ups", "author", "stickied"]


# TODO: Create a Scraper class to hold auth and rate_limit information
def get_auth_headers():
    # Set a User-Agent header -- This is how you identify yourself
    user_agent = f"script:{cfg.NAME}:{cfg.VERSION} (by /u/{cfg.REDDIT_USERNAME})" # <platform>:<app ID>:<version string> (by /u/<reddit username>)
    headers = { "User-Agent": user_agent }

    # OAUTH
    response = requests.post(
        ACCESS_ENDPOINT,
        data = {"grant_type":"client_credentials"},
        auth = (cfg.CLIENT_ID, cfg.CLIENT_SECRET),
        headers=headers
    )
    auth = response.json()
    # print(auth)

    access_token = auth["access_token"]

    headers = {**headers, **{"Authorization": f"Bearer {access_token}"}}
    return headers


def get_rate_limit(response_headers: dict):
    rate_limit = {
        "used": response_headers["X-Ratelimit-Used"],
        "remaining": response_headers["X-Ratelimit-Remaining"],
        "reset": response_headers["X-Ratelimit-Reset"],
    }
    return rate_limit


def print_rate_limit_info(rate_limit: dict):
    used = rate_limit["used"]
    remaining = rate_limit["remaining"]
    reset = rate_limit["reset"]
    print(f"Used {used} -- {remaining} remaining. Rate limit resets in {reset} seconds.\n")


# TODO: DRY if possible here...
def get_top_posts(headers: dict, subreddit: str, limit: int):
    endpoint = f"{OAUTH_ENDPOINT}/r/{subreddit}/top/.json"
    params = {"limit": limit}
    api_response = requests.get(
        endpoint,
        headers=headers,
        params=params
    )
    # rate_limit = get_rate_limit(api_response.headers)
    # print_rate_limit_info(rate_limit)
    # print(api_response.url)
    api_response_data = api_response.json()

    if cfg.DUMP_JSON:
        with open(f"{subreddit}_top.json", "w") as outfile:
            json.dump(api_response_data, outfile, indent=4)

    posts = api_response_data["data"]["children"]
    data = []
    for post in posts:
        post_kind = post["kind"]
        post_data = post["data"]
        values = [post_data[column] for column in POST_COLUMNS]
        data.append([post_kind, *values])

    df = pd.DataFrame(data, columns=["kind", *POST_COLUMNS])
    return df


def get_post_top_comments(headers: dict, subreddit: str, post_id: str, limit: int):
    endpoint = f"{OAUTH_ENDPOINT}/r/{subreddit}/comments/{post_id}/.json"
    params = {
        "sort": "top",
        "limit": limit,
        "showmore": False
    }
    api_response = requests.get(
        endpoint,
        headers=headers,
        params=params
    )
    # rate_limit = get_rate_limit(api_response.headers)
    # print_rate_limit_info(rate_limit)
    api_response_data = api_response.json()

    if cfg.DUMP_JSON:
        with open(f"{subreddit}_{post_id}_comments.json", "w") as outfile:
            json.dump(api_response_data, outfile, indent=4)

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
    headers = get_auth_headers()
    
    # TODO: Check out live threads: https://www.reddit.com/dev/api/#section_live

    for subreddit in SUBREDDITS:
        top_posts_df = get_top_posts(headers, subreddit, POST_LIMIT)
        print(top_posts_df)
        print()
        top_comments_dfs = []
        for i, row in top_posts_df.iterrows():
            top_comments_df = get_post_top_comments(headers, subreddit, row["id"], COMMENT_LIMIT)
            top_comments_dfs.append(top_comments_df)
        
        all_top_comments_df = pd.concat(top_comments_dfs, sort=False)
        print(all_top_comments_df)
        print()


if __name__ == "__main__":
    main()