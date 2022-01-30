import requests
import json
import pandas as pd

import config as cfg


ACCESS_ENDPOINT = "https://www.reddit.com/api/v1/access_token"
OAUTH_ENDPOINT = "https://oauth.reddit.com"
SUBREDDITS=[
    "nfl",
    "buffalobills",
    "49ers"
]

def get_top_posts(headers: dict, subreddit: str):
    API_ENDPOINT = f"{OAUTH_ENDPOINT}/r/{subreddit}/top/.json"
    params = {"count": 10}
    api_response = requests.get(
        API_ENDPOINT,
        headers=headers,
        params=params
    )
    api_response_data = api_response.json()

    ## Prints json
    # print(json.dumps(api_response_data))

    posts = api_response_data["data"]["children"]
    data = []
    columns = ["ups", "title"]
    for post in posts:
        post_data = post["data"]
        title = post_data["title"]
        ups = post_data["ups"]
        data.append([ups, title])

    df = pd.DataFrame(data, columns=columns)
    return df

def main():
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
    # response_headers = response.headers
    # rate_info = f"Used {response_headers["X-Ratelimit-Used"]} "
    # print(response_headers["X-Ratelimit-Used"])
    # print(response_headers["X-Ratelimit-Remaining"])
    # print(response_headers["X-Ratelimit-Reset"])

    access_token = auth["access_token"]

    headers = {**headers, **{"Authorization": f"Bearer {access_token}"}}
    
    for subreddit in SUBREDDITS:
        df = get_top_posts(headers, subreddit)
        print(f"----- {subreddit} -----")
        print(df)
        print()


if __name__ == "__main__":
    main()