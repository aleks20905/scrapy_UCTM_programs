from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

def wait_for_ajax(driver):
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except:
        pass

driver = webdriver.Chrome()
driver.get('https://curriculum.uctm.edu')

try:
    with open("all_schedules.txt", "w", encoding="utf-8") as file:
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

                                file.write(f"Course: {course_text} (Value: {course_value})\n")
                                file.write(f"Spec: {spec_text} (Value: {spec_value})\n")
                                file.write(f"Group: {group_text} (Value: {group_value})\n")
                                file.write("Schedule:\n")

                                # Extract schedule data
                                schedule_items = driver.find_elements(By.CLASS_NAME, "fc-list-table")
                
                                # Find all the rows in the table
                                items = schedule_items.find_elements(By.CSS_SELECTOR, "tr")
                                
                                for item in items:
                                    time = item.find_element(By.CLASS_NAME, "fc-list-item-time").text
                                    title = item.find_element(By.CLASS_NAME, "fc-list-item-title").text
                                    print(f"  {time}: {title}\n")
                                    file.write(f"  {time}: {title}\n")

                                file.write("\n" + "="*40 + "\n\n")
            break

finally:
    driver.quit()