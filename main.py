import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

# Initialize the WebDriver (e.g., Chrome)
driver = webdriver.Chrome()
driver.get('https://curriculum.uctm.edu')

# Initialize the SQLite database connection
conn = sqlite3.connect('schedules_selnim.db')
cursor = conn.cursor()

# Create the tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_text TEXT,
    course_value TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS specifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    spec_text TEXT,
    spec_value TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id INTEGER,
    group_text TEXT,
    group_value TEXT,
    FOREIGN KEY(spec_id) REFERENCES specifications(id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    date TEXT,
    title TEXT,
    time TEXT,
    type TEXT,
    hall TEXT,
    teacher TEXT,
    FOREIGN KEY(group_id) REFERENCES groups(id)
)''')

def wait_for_ajax(driver):
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except:
        pass

def close_panel_if_open(driver):
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "jsPanel-btn-close"))
        )
        close_button.click()
        wait_for_ajax(driver)
    except:
        pass

try:
    # Switch to "График" view
    list_view_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "fc-listWeek-button"))
    )
    list_view_button.click()
    wait_for_ajax(driver)

    course_select = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "course"))
    )
    course_options = course_select.find_elements(By.TAG_NAME, "option")
    
    for course_option in course_options:
        course_value = course_option.get_attribute("value")
        course_text = course_option.text
        
        if course_value:
            Select(course_select).select_by_value(course_value)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", course_select)
            wait_for_ajax(driver)
            
            # Insert the course into the database
            cursor.execute("INSERT INTO courses (course_text, course_value) VALUES (?, ?)", (course_text, course_value))
            course_id = cursor.lastrowid
            
            spec_select = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "spec"))
            )
            spec_options = spec_select.find_elements(By.TAG_NAME, "option")

            for spec_option in spec_options:
                spec_value = spec_option.get_attribute("value")
                spec_text = spec_option.text
                
                if spec_value:
                    Select(spec_select).select_by_value(spec_value)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", spec_select)
                    wait_for_ajax(driver)

                    # Insert the specification into the database
                    cursor.execute("INSERT INTO specifications (course_id, spec_text, spec_value) VALUES (?, ?, ?)", (course_id, spec_text, spec_value))
                    spec_id = cursor.lastrowid
                    
                    group_select = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "group"))
                    )
                    group_options = group_select.find_elements(By.TAG_NAME, "option")
                    
                    for group_option in group_options:
                        group_value = group_option.get_attribute("value")
                        group_text = group_option.text
                        
                        if group_value and group_text:
                            Select(group_select).select_by_value(group_value)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", group_select)
                            wait_for_ajax(driver)

                            # Insert the group into the database
                            cursor.execute("INSERT INTO groups (spec_id, group_text, group_value) VALUES (?, ?, ?)", (spec_id, group_text, group_value))
                            group_id = cursor.lastrowid

                            # Handle StaleElementReferenceException with a retry mechanism
                            retry_count = 3
                            while retry_count > 0:
                                try:
                                    schedule_table = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "fc-list-table"))
                                    )

                                    items = schedule_table.find_elements(By.CSS_SELECTOR, "tr")
                                    
                                    for item in items:
                                        if "fc-list-item" in item.get_attribute("class"):
                                            # Ensure previous panel is closed before interacting with a new item
                                            close_panel_if_open(driver)

                                            # Click on the item to reveal additional information
                                            item.click()
                                            wait_for_ajax(driver)
                                            
                                            # Extract additional information
                                            panel_content = WebDriverWait(driver, 10).until(
                                                EC.presence_of_element_located((By.CLASS_NAME, "jsPanel-content"))
                                            )
                                            
                                            course_title = panel_content.find_element(By.ID, "te").text
                                            course_time = panel_content.find_element(By.XPATH, "//div[@class='row'][2]/div[@id='d']").text
                                            course_type = panel_content.find_element(By.ID, "t").text
                                            course_hall = panel_content.find_element(By.ID, "ihall").text
                                            course_teacher = panel_content.find_element(By.ID, "iteacher").text
                                            
                                            # Insert the schedule into the database
                                            cursor.execute('''INSERT INTO schedule 
                                                (group_id, date, title, time, type, hall, teacher) 
                                                VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                                                (group_id, date, course_title, course_time, course_type, course_hall, course_teacher)
                                            )
                                            
                                        if "fc-list-heading" in item.get_attribute("class"):
                                            date = item.get_attribute("data-date")
                                            # Update the date in the schedule table
                                            cursor.execute('''UPDATE schedule SET date = ? WHERE group_id = ? AND date IS NULL''', 
                                                (date, group_id)
                                            )
                                            
                                    break  # Break the retry loop if successful

                                except StaleElementReferenceException:
                                    retry_count -= 1
                                    print("Stale element reference, retrying...")

                                except ElementClickInterceptedException:
                                    print("Element click intercepted, trying to close the panel and retry...")
                                    close_panel_if_open(driver)
                                    retry_count -= 1

finally:
    # Commit the changes and close the database connection
    conn.commit()
    conn.close()
    driver.quit()
