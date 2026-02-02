import requests
import time

def get_reddit_posts(subreddit, limit=25):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    # WICHTIG: Ein einzigartiger User-Agent, sonst blockt Reddit sofort
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Thesis-Scraper/1.0'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        posts = data['data']['children']
        for post in posts:
            title = post['data']['title']
            text = post['data']['selftext']
            print(f"TITEL: {title}\nTEXT: {text[:100]}...\n---")
    else:
        print(f"Error: {response.status_code}")

# Testlauf
get_reddit_posts("MachineLearning")