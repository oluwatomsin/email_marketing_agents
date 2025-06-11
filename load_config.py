from rich import print
import requests



url = "https://linkedin-data-api.p.rapidapi.com/get-profile-data-by-url"
querystring = {"url": "https://www.linkedin.com/in/kevinschlack"}

headers = {
    "x-rapidapi-key": "99a8bdab1emsh976f11e036ef5fep18bf00jsnd9124fe05900",
    "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
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

print(lead_info)
