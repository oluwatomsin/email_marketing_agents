import requests
from rich import print
from bs4 import BeautifulSoup


class TextExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/117.0.0.0 Safari/537.36"
            )
        }

    def from_website(self, web_url: str) -> str:
        try:
            response = requests.get('https://www.' + web_url, headers=self.headers, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()

            text = soup.get_text(separator='\n')
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return '\n'.join(lines)

        except requests.exceptions.RequestException as e:
            return f"Error fetching the website: {e}"

    def from_txt(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            print(f"File not found: {path}")
            return ""
        except Exception as e:
            print(f"Error reading file: {e}")
            return ""
