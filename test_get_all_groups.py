import requests
import re
import json

# URL of the JavaScript file
url = "https://curriculum.uctm.edu/js/opp.js"

# Fetch the JavaScript file
response = requests.get(url)

if response.status_code == 200:
    js_content = response.text
    print("JavaScript file fetched successfully!")

    # Find all occurrences of the sp2m variable
    pattern = re.compile(r'(?:const|let|var)\s+sp2m\s*=\s*\[(.*?)\]', re.DOTALL)
    matches = pattern.findall(js_content)

    if matches:
        # Extract and clean the sp2m variable
        sp2m_string = matches[0]
        sp2m_string = sp2m_string.replace('\n', '').replace('\r', '')  # Remove newlines
        sp2m_string = f'[{sp2m_string}]'  # Ensure it's enclosed in brackets

        try:
            # Convert to JSON
            sp2m_list = json.loads(sp2m_string)
            
            courses = []
            for i, entry in enumerate(sp2m_list):
                # Split and clean the course data
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
                    'course': f'{i+1}',
                    'data': structured_data
                }
                courses.append(course_data)

            # Convert to structured JSON and save to file
            json_output = json.dumps(courses, ensure_ascii=False, indent=2)
            with open('courses_data.json', 'w', encoding='utf-8') as f:
                f.write(json_output)
            print("Converted sp2m to JSON successfully and saved to 'courses_data.json'!")
            
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
    else:
        print("sp2m variable not found in the JavaScript file.")
else:
    print(f"Failed to fetch JavaScript file. Status code: {response.status_code}")
