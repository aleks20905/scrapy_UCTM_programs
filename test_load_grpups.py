import requests
import json

# Function to fetch group data based on course and spec
def fetch_current_groups(course, spec):
    url = "https://curriculum.uctm.edu/load_groups_db.php"
    headers = {
        "accept": "*/*",
        "accept-language": "en,bg-BG;q=0.9,bg;q=0.8",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest"
    }
    data = {
        "course": course,
        "fo": "true",
        "spec": spec
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        try:
            group_data = response.json()
            # Extract all currentGroup values
            groups = [group.get('currentGroup') for group in group_data if 'currentGroup' in group]
            return groups
        except json.JSONDecodeError:
            print(f"Failed to decode JSON for course {course}, spec {spec}.")
            return None
    else:
        print(f"Request failed for course {course}, spec {spec} with status code: {response.status_code}.")
        return None

# Load the JSON data from file
with open('courses_data.json', 'r', encoding='utf-8') as file:
    courses = json.load(file)

# Iterate through courses and specs, and add currentGroups
for course in courses:
    course_number = course["course"]
    for spec in course["data"]:
        spec_acronym = spec["spec"]
        # Fetch the currentGroups for the spec
        current_groups = fetch_current_groups(course_number, spec_acronym)
        if current_groups:
            spec["currentGroups"] = current_groups

# Save the updated data back to the JSON file
with open('courses_data_with_groups.json', 'w', encoding='utf-8') as file:
    json.dump(courses, file, ensure_ascii=False, indent=2)

print("Updated JSON data with currentGroups saved to 'courses_data_with_groups.json'.")
