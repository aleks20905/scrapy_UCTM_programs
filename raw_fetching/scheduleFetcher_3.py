import requests
import json

# Function to fetch schedule information based on course, group, and spec
def fetch_schedule_info(course, group, spec, start_date, end_date):
    url = "https://curriculum.uctm.edu/load_schedul_info.php"
    headers = {
        "accept": "*/*",
        "accept-language": "en,bg-BG;q=0.9,bg;q=0.8",
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }
    data = {
        "studyForm": "true",
        "course": course,
        "group": group,
        "spec": spec,
        "start": start_date,
        "end": end_date
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        try:
            schedule_data = response.json()
            return schedule_data
        except json.JSONDecodeError:
            print(f"Failed to decode JSON for course {course}, spec {spec}, group {group}.")
            return None
    else:
        print(f"Request failed for course {course}, spec {spec}, group {group} with status code: {response.status_code}.")
        return None

# Load the JSON data with courses and specifications
with open('courses_data_with_groups.json', 'r', encoding='utf-8') as file:
    courses = json.load(file)

# Prepare a list to store all schedule information
all_schedules = []

# Define date range
start_date = "2024-05-20T00:00:00+03:00"
end_date = "2024-05-25T00:00:00+03:00"

# Iterate through courses and specs to fetch schedule info
for course in courses:
    course_number = course["course"]
    for spec in course["data"]:
        spec_acronym = spec["spec"]
        for group in spec.get("currentGroups", []):
            schedule_info = fetch_schedule_info(course_number, group, spec_acronym, start_date, end_date)
            if schedule_info:
                for event in schedule_info:
                    event["course"] = course_number
                    event["spec"] = spec_acronym
                    event["group"] = group
                all_schedules.extend(schedule_info)

# Save the schedule data to a JSON file
with open('schedules_data.json', 'w', encoding='utf-8') as file:
    json.dump(all_schedules, file, ensure_ascii=False, indent=2)

print("Schedule data has been fetched and saved to 'schedules_data.json'.")
