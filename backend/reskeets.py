# reskeets.py

import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables (e.g., BLUESKY_USERNAME, BLUESKY_PASSWORD)
load_dotenv()
USERNAME = os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_PASSWORD")

BLSKY_API = "https://bsky.social/xrpc"
SESSION_ENDPOINT = f"{BLSKY_API}/com.atproto.server.createSession"
REPOSTS_ENDPOINT = f"{BLSKY_API}/app.bsky.feed.getRepostedBy"
POST_THREAD_ENDPOINT = f"{BLSKY_API}/app.bsky.feed.getPostThread"
HANDLE_RESOLVE_ENDPOINT = f"{BLSKY_API}/com.atproto.identity.resolveHandle"

def authenticate(username, password):
    res = requests.post(SESSION_ENDPOINT, json={"identifier": username, "password": password})
    res.raise_for_status()
    return res.json()["accessJwt"]

def extract_post_uri(post_url):
    parsed = urlparse(post_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 4 or parts[2] != "post":
        raise ValueError("Invalid Bluesky post URL format.")
    handle = parts[1]
    rkey = parts[3]

    res = requests.get(HANDLE_RESOLVE_ENDPOINT, params={"handle": handle})
    res.raise_for_status()
    did = res.json()["did"]

    return f"at://{did}/app.bsky.feed.post/{rkey}"

def get_post_data(uri, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(POST_THREAD_ENDPOINT, params={"uri": uri}, headers=headers)
    res.raise_for_status()
    post = res.json()["thread"]["post"]
    return {
        "text": post["record"]["text"],
        "replies": post.get("replyCount", 0),
        "reposts": post.get("repostCount", 0),
        "likes": post.get("likeCount", 0)
    }

def get_reposts(uri, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(REPOSTS_ENDPOINT, params={"uri": uri}, headers=headers)
    res.raise_for_status()
    return res.json().get("repostedBy", [])

# This is the function to import in nodos.py
def fetch_reposts_data(post_url):
    token = authenticate(USERNAME, PASSWORD)
    uri = extract_post_uri(post_url)
    original_post = get_post_data(uri, token)
    reposts = get_reposts(uri, token)

    reposts_data = []
    for reposter in reposts:
        if not reposter.get("did") or not reposter.get("handle"):
            continue
        reposts_data.append({
            "type": "repost",
            "id": f"repost_{reposter.get('did')}_{uri}",
            "author": reposter.get("handle"),
            "author_display_name": reposter.get("displayName") or reposter.get("handle"),
            "parent_id": uri,
            "text": original_post["text"],
            "created_at": reposter.get("indexedAt"),  # May be None
            "metrics": {
                "replies": 0,  # Reposts don't carry their own counts
                "reposts": 0,
                "likes": 0
            }
        })
    return reposts_data
