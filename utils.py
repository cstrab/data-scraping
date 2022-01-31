import urllib


def encoded_url(url: str, params: dict):
    if len(params) > 0:
        encoded = urllib.parse.urlencode(params)
        url += f"?{encoded}"
    return url