from arxiv_extract import access_web_extract
import requests
import os

# Extracting info from Arxiv
WEB_URL = input("Please enter the URL")
PARSER = "html.parser"
scraping = access_web_extract(WEB_URL, PARSER)
title, authors, doi, conference_journal, published_year = scraping.implement()


# Notion API
api_token = os.environ["NOTION_API_TOKEN"]
database_id = os.environ["PAPERS_DATABASE_ID"]


post_endpoint = "https://api.notion.com/v1/pages"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
    "Authorization": "Bearer " + api_token,
}

json_data = {
    "parent": {"type": "database_id", "database_id": database_id},
    "properties": {
        "Important": {"checkbox": False},
        "Read": {"checkbox": False},
        "Title": {"title": [{"text": {"content": title}}]},
        "Authors": {"rich_text": [{"text": {"content": authors}}]},
        "Abstract": {"rich_text": [{"text": {"content": ""}}]},
        "Journal/Conference": {"multi_select": [{"name": conference_journal}]},
        "Year": {"number": int(published_year)},
        "doi": {"url": doi},
    },
}

response = requests.post(post_endpoint, json=json_data, headers=headers)
print(response.json())
