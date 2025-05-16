import requests
from rich import print
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()


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
            response = requests.get('https://www.' + web_url, headers=self.headers)
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


class JobPostProfileExtractor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('RAPID_API_KEY')

    def get_linkedin_job(self, job_url: str) -> str:
        job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
        job_id = job_id_match.group(1) if job_id_match else None
        if not job_id:
            return "Null, Kindly check the URL. It seems to be invalid"

        endpoint = "https://linkedin-data-api.p.rapidapi.com/get-job-details"
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
        }
        querystring = {"id": job_id}

        response = requests.get(endpoint, headers=headers, params=querystring)
        if response.status_code == 200:
            output = response.json()
            return (
                f"Company Name: {output['data']['company']['name']}\n\n"
                f"Job Title: {output['data']['title']}\n\n"
                f"Job Description:\n{output['data']['description']}"
            )
        else:
            print("Error:", response.json())
            return "Null"

    def get_glassdoor_job(self, job_url: str) -> str:
        job_id_match = re.search(r'jobListingId=(\d+)', job_url)
        listing_id = job_id_match.group(1) if job_id_match else None
        print(listing_id)
        query_match = re.search(r'\?(pos=.*)', job_url)
        query_string = query_match.group(1) if query_match else None
        print(query_string)

        if not listing_id or not query_string:
            return "Null, Invalid Glassdoor URL"

        endpoint = "https://glassdoor-real-time.p.rapidapi.com/jobs/details"
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "glassdoor-real-time.p.rapidapi.com"
        }
        querystring = {
            "listingId": listing_id,
            "queryString": query_string
        }

        response = requests.get(endpoint, headers=headers, params=querystring)
        if response.status_code == 200:
            description_html = response.json()['data']['job']['description']
            soup = BeautifulSoup(description_html, "html.parser")
            return soup.get_text(separator="\n", strip=True)
        else:
            print("Error:", response.json())
            return "Null"

    def get_profile_info(self, profile_url):
        url = "https://linkedin-data-api.p.rapidapi.com/get-profile-data-by-url"
        querystring = {"url": f"{profile_url}"}

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()

            positions_data = data.get("position", [])

            # Extract only the fields you care about
            filtered_positions = []
            for pos in positions_data:
                filtered_positions.append({
                    "companyName": pos.get("companyName"),
                    "companyIndustry": pos.get("companyIndustry"),
                    "title": pos.get("title"),
                    "description": pos.get("description"),
                    "employmentType": pos.get("employmentType"),
                    "start": pos.get("startsAt"),
                    "end": pos.get("endsAt")
                })

            lead_info = {
                'f_name': data.get("firstName"),
                'l_name': data.get("lastName"),
                'summary': data.get("summary"),
                'positions': filtered_positions
            }

            return lead_info
        else:
            print("Error:", response.json())
            return "Null"


    def parse_job_url(self, job_url: str) -> str:
        if 'linkedin' in job_url:
            return self.get_linkedin_job(job_url)
        elif 'glassdoor' in job_url:
            return self.get_glassdoor_job(job_url)
        else:
            return "Unsupported URL. Only LinkedIn and Glassdoor are supported at the moment."
