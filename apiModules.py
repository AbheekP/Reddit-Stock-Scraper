import requests
from dotenv import load_dotenv
import os

load_dotenv()

redditPublicKey = os.getenv('REDDIT_PUBLIC_KEY')
redditPrivateKey = os.getenv('REDDIT_PRIVATE_KEY')
finnhubToken = os.getenv('FINNHUB_TOKEN')
alphaVantageToken = os.getenv('ALPHAVANTAGE_TOKEN')

# Reddit API authentication
def authenticateRedditAPI(username, password):
    auth = requests.auth.HTTPBasicAuth(redditPublicKey, redditPrivateKey)
    data = {"grant_type" : "password",
            "username"   : username,
            "password"   : password}
    headers = {"User-Agent": "Stock Searcher"}

    res = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)
    TOKEN = res.json()['access_token']
    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}
    
    return headers

# Searches reddit posts
def redditPostSearchExecution(subreddit: str, filter: str, timeframe: str, headers, limit=25):
    base = "https://oauth.reddit.com/r/"
    url = base + subreddit + "/" + filter + "/"
    
    if(filter == 'top'):
        url += '?t=' + timeframe
    
    url = url.lower()
    return requests.get(url, headers=headers, params={'limit': str(limit)})

# Searches reddit users
def redditUserSearchExecution(username:str, headers):
    url = "https://oauth.reddit.com/user/%s/about" % (username)
    return requests.get(url, headers=headers)

# Finnhub search execution
def finnhubExecution(query):
    base = "https://finnhub.io/api/v1/"
    token = f"&token={finnhubToken}"

    url = base + query + token
    results = requests.get(url)
    return results

# Alpha Vantage Search Execution
def alphaVantageExecution(query, compact=False):
    base = "https://www.alphavantage.co/query?"
    token = f"&apikey={alphaVantageToken}"

    if(compact):
        query += "&outputsize=compact"
    else:
        query += "&outputsize=full"

    url = base + query + token
    return requests.get(url)
