import requests
import json
import re

# Function to fetch current groups for a given course and spec
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

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raises HTTPError for bad responses
        group_data = response.json()
        groups = [group.get('currentGroup') for group in group_data if 'currentGroup' in group]
        return groups
    except requests.RequestException as e:
        print(f"Error fetching groups for course {course}, spec {spec}: {e}")
        return None

# Function to fetch schedule information for a given course, group, and spec
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

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raises HTTPError for bad responses
        schedule_data = response.json()
        return schedule_data
    except requests.RequestException as e:
        print(f"Error fetching schedule for course {course}, spec {spec}, group {group}: {e}")
        return None

# Load the JSON data with courses and specifications
def load_courses(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# Save cleaned schedule data to a JSON file
def save_schedule_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

# Main function to orchestrate the tasks
def main():
    # Load course and spec data
    courses_file = 'courses_data_with_groups.json'
    courses = load_courses(courses_file)
    print(f"Loaded courses data from {courses_file}.")

    # Define date range for schedule
    start_date = "2024-05-20T00:00:00+03:00"
    end_date = "2024-05-25T00:00:00+03:00"

    all_schedules = []

    # Iterate through courses and specs to fetch schedule info
    for course in courses:
        course_number = course["course"]
        print(f"Processing course {course_number}...")
        for spec in course["data"]:
            spec_acronym = spec["spec"]
            print(f"  Fetching groups for spec {spec_acronym}...")
            current_groups = fetch_current_groups(course_number, spec_acronym)
            if current_groups:
                for group in current_groups:
                    print(f"    Fetching schedule for group {group}...")
                    schedule_info = fetch_schedule_info(course_number, group, spec_acronym, start_date, end_date)
                    if schedule_info:
                        for event in schedule_info:
                            # Remove unwanted fields
                            event.pop('id', None)
                            event.pop('id_rcd', None)
                            event.pop('studyForm', None)
                            event.pop('color', None)
                            # Add extra context
                            event["course"] = course_number
                            event["spec"] = spec_acronym
                            event["group"] = group
                        all_schedules.extend(schedule_info)
            else:
                print(f"    No groups found for spec {spec_acronym}.")

    # Save the collected schedule data
    output_file = 'schedules_data.json'
    save_schedule_data(output_file, all_schedules)
    print(f"Schedule data has been saved to {output_file}.")

if __name__ == "__main__":
    main()
