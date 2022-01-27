import requests


from config import CLIENT_ID, CLIENT_SECRET, NAME, VERSION, REDDIT_USERNAME


ACCESS_ENDPOINT = "https://www.reddit.com/api/v1/access_token"
SUBREDDIT="TellMeAFact"

def main():

    # Set a User-Agent header -- This is how you identify yourself
    user_agent = f"script:{NAME}:{VERSION} (by /u/{REDDIT_USERNAME})" # <platform>:<app ID>:<version string> (by /u/<reddit username>)
    headers = {
        "User-Agent": user_agent
    }

    # OAUTH
    response = requests.post(
        ACCESS_ENDPOINT,
        data = {"grant_type":"client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers=headers
    )
    auth = response.json()
    # print(auth)
    # response_headers = response.headers
    # print(response_headers["X-Ratelimit-Used"])
    # print(response_headers["X-Ratelimit-Remaining"])
    # print(response_headers["X-Ratelimit-Reset"])

    access_token = auth["access_token"]

    headers = {**headers, **{"Authorization": f"Bearer {access_token}"}}
    
    # API Request
    # API_ENDPOINT = "https://oauth.reddit.com/api/v1/me"
    API_ENDPOINT = f"https://oauth.reddit.com/r/{SUBREDDIT}/top/.json"
    params = {"count": 1}
    api_response = requests.get(
        API_ENDPOINT,
        headers=headers,
        params=params
    )
    api_response_data = api_response.json()
    print(api_response_data)


if __name__ == "__main__":
    main()
