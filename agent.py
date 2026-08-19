import requests
import json
from bs4 import BeautifulSoup

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "qwen3:8b"

def load_skill(name):
    with open(f"skills/{name}.md") as f:
        return f.read()

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

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the internet and return relevant web pages. "
                "Use this whenever information from the internet is required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search the web for"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": (
                "Open a web page and extract its readable text. "
                "Use this when you need to inspect a specific URL."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to open"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

def ask_qwen(prompt):
    skill = load_skill("find_b2b_partners")
    messages = [
     {
             "role": "system",
             "content": """
         You are an autonomous research agent.   
     
         You can use tools to gather information.
         Use tools when necessary.
         Do not invent information.
         When you have enough information, answer the user.
         """
        },
        {
            "role": "system",
            "content": skill
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    while True:
        response = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL_NAME,
            "messages": messages,
            "tools": tools,
            "stream": False
        })

        asistant_message = response.json()['message']
        messages.append(asistant_message)
        if "tool_calls" not in asistant_message:
            return asistant_message["content"]

        for tool_call in asistant_message["tool_calls"]:
            function = tool_call["function"]
            name = function["name"]
            arguments = function["arguments"]
            print(f"\n[TOOL] {name}({arguments})")
            if name == "search_web":
                result = search_web(**arguments)
            elif name == "open_url":
                result = open_url(**arguments)
            else:
                result = "Unknown tool"
            print(f"[RESULT] {result}")
            messages.append({
                "role": "tool",
                "content": json.dumps(result),
            })

while True:
    prompt = input("Enter a prompt: ")
    if prompt == "exit":
        break
    response = ask_qwen(prompt)
    print(response)
