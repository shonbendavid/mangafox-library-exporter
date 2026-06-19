import requests
from requests.exceptions import RequestException

def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def clean_text(text):
    return ' '.join(text.split())

def save_to_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)