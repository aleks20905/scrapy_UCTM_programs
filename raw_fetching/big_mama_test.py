import requests
import json
import re
import sys
import sqlite3
from datetime import datetime

def fetch_js_data(url):
    """Fetch JavaScript file and extract course and spec data."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        js_content = response.text

        # Extract the sp2m variable content
        pattern = re.compile(r'(?:const|let|var)\s+sp2m\s*=\s*\[(.*?)\]', re.DOTALL)
        matches = pattern.findall(js_content)

        if not matches:
            print("Error: sp2m variable not found in JavaScript file.")
            return None

        sp2m_string = matches[0].replace('\n', '').replace('\r', '')  # Remove newlines
        sp2m_string = f'[{sp2m_string}]'  # Ensure it's enclosed in brackets

        sp2m_list = json.loads(sp2m_string)

        # Parse course and spec data
        courses = []
        for i, entry in enumerate(sp2m_list):
            course_elements = [item.strip() for item in entry.split(';') if item.strip()]
            structured_data = []
            for element in course_elements:
                if ':' in element:
                    acronym, name = element.split(':', 1)
                    acronym = acronym.strip()
                    name = name.strip()
                    structured_data.append({
                        'spec': acronym,
                        'spec_name': name
                    })

            course_data = {
                'course': str(i + 1),
                'data': structured_data
            }
            courses.append(course_data)

        return courses

    except requests.RequestException as e:
        print(f"Error fetching JavaScript file: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def fetch_current_groups(course, spec):
    """Fetch current groups for a given course and spec."""
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
        response.raise_for_status()  # Check for HTTP errors
        group_data = response.json()
        groups = [group.get('currentGroup') for group in group_data if 'currentGroup' in group]
        return groups
    except requests.RequestException as e:
        print(f"Error fetching groups for course {course}, spec {spec}: {e}")
        return None

def fetch_schedule_info(course, group, spec, start_date, end_date):
    """Fetch schedule information for a given course, group, and spec."""
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
        response.raise_for_status()  # Check for HTTP errors
        schedule_data = response.json()
        return schedule_data
    except requests.RequestException as e:
        print(f"Error fetching schedule for course {course}, spec {spec}, group {group}: {e}")
        return None

def create_database():
    """Create SQLite database and tables."""
    conn = sqlite3.connect('schedules.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course TEXT,
        spec TEXT,
        group_name TEXT,
        title TEXT,
        start TEXT,
        end TEXT,
        room TEXT,
        teacher TEXT,
        type TEXT,
        group_s TEXT,
        des TEXT
    )
    ''')
    
    conn.commit()
    return conn

def save_schedule_data(conn, data):
    """Save schedule data to SQLite database."""
    cursor = conn.cursor()
    
    for event in data:
        cursor.execute('''
        INSERT INTO schedules (course, spec, group_name, title, start, end, room, teacher, type, group_s, des)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event['course'],
            event['spec'],
            event['group'],
            event.get('title', ''),
            event.get('start', ''),
            event.get('end', ''),
            event.get('hall', ''),
            event.get('teacher', ''),
            event.get('studyType', ''),
            event.get('group_s', ''),
            event.get('des', '')
        ))
    
    conn.commit()
    
def main():
    js_url = "https://curriculum.uctm.edu/js/opp.js"

    print("Fetching JavaScript file and extracting course data...")
    courses = fetch_js_data(js_url)
    if not courses:
        print("Failed to fetch or parse course data.")
        sys.exit(1)
    print("Course data loaded successfully.")

    # Define date range for schedule
    start_date = "2024-05-20T00:00:00+03:00"
    end_date = "2024-05-25T00:00:00+03:00"

    # Create SQLite database
    conn = create_database()

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
                    try:
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
                            # Save the schedule data to SQLite
                            save_schedule_data(conn, schedule_info)
                        else:
                            print(f"    No schedule info found for group {group}.")
                    except Exception as e:
                        print(f"    Error processing group {group}: {str(e)}")
            else:
                print(f"    No groups found for spec {spec_acronym}.")

    # Close the database connection
    conn.close()
    print("Schedule data has been saved to the SQLite database 'schedules.db'.")

if __name__ == "__main__":
    main()