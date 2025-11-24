import requests
from duckduckgo_search import DDGS
import wikipediaapi
import yfinance as yf
from os import getenv

# 1) DuckDuckGo search wrapper

def search_company(query, max_results=8):
    results = []
    with DDGS() as ddgs:
        ddg_results = ddgs.text(
            keywords=query,
            region="wt-wt",
            safesearch="moderate",
            timelimit=None,
            backend="auto",
            max_results=max_results
        )
        for r in ddg_results:
            results.append({
                "title": r.get("title"),
                "body": r.get("body"),
                "href": r.get("href")
            })
    return results

# 2) NewsAPI wrapper


NEWSAPI_BASE = "https://newsapi.org/v2/everything"
NEWSAPI_KEY = getenv('NEWSAPI_KEY')


def get_latest_news(company, page_size=5):
    if not NEWSAPI_KEY:
        return []
    params = {
        'q': company,
        'pageSize': page_size,
        'sortBy': 'relevancy',
        'language': 'en',
        'apiKey': NEWSAPI_KEY
    }
    r = requests.get(NEWSAPI_BASE, params=params, timeout=15)
    data = r.json()
    articles = data.get('articles', [])
    brief = []
    for a in articles:
        brief.append({
            'title': a.get('title'),
            'source': a.get('source', {}).get('name'),
            'description': a.get('description'),
            'url': a.get('url')
        })
    return brief


# 3) Wikipedia summary


wiki_wiki = wikipediaapi.Wikipedia(user_agent = 'research_agent (crdiksharaghu@gmail.com)',language='en')


def get_wikipedia_summary(name, sentences=3):
    page = wiki_wiki.page(name)
    if not page.exists():
        return None
    summary = page.summary[0:1000]
    return summary


# 4) Financials via yfinance


def get_financials(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            'market_cap': info.get('marketCap'),
            'employees': info.get('fullTimeEmployees'),
            'longBusinessSummary': info.get('longBusinessSummary'),
            'sector': info.get('sector'),
            'industry': info.get('industry')
            }
    except Exception:
        return None