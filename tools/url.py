import requests
from bs4 import BeautifulSoup

def search_web(query):

    response = requests.get(
        "http://localhost:8888/search",
        params={
            "q": query,
            "format": "json"
        }
    )

    response.raise_for_status()

    data = response.json()

    return [
        {
            "title": result["title"],
            "url": result["url"],
            "content": result.get("content", "")
        }
        for result in data["results"]
    ]

def open_url(url):
    response = requests.get(
        url,
        timeout=15,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer"
    ]):
        element.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return {
        "url": url,
        "content": text[:15000]
    }
