from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

# Initialize the WebDriver (e.g., Chrome)
driver = webdriver.Chrome()
driver.get('https://curriculum.uctm.edu')

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
        # If close button is not found, it might mean the panel is already closed or doesn't exist
        pass

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

                                                # Click on the item to reveal additional information
                                                item.click()
                                                wait_for_ajax(driver)
                                                
                                                # Extract additional information
                                                panel_content = WebDriverWait(driver, 10).until(
                                                    EC.presence_of_element_located((By.CLASS_NAME, "jsPanel-content"))
                                                )
                                                
                                                # Extract data from the panel
                                                course_title = panel_content.find_element(By.ID, "te").text
                                                course_time = panel_content.find_element(By.XPATH, "//div[@class='row'][2]/div[@id='d']").text
                                                course_type = panel_content.find_element(By.ID, "t").text
                                                course_hall = panel_content.find_element(By.ID, "ihall").text
                                                course_teacher = panel_content.find_element(By.ID, "iteacher").text
                                                
                                                # file.write(f"  {time}: {title}\n")
                                                file.write(f"    Title: {course_title}\n")
                                                file.write(f"    Time: {course_time}\n")
                                                file.write(f"    Type: {course_type}\n")
                                                file.write(f"    Hall: {course_hall}\n")
                                                file.write(f"    Teacher: {course_teacher}\n")
                                                
                                                close_panel_if_open(driver)
                                                
                                                
                                            if "fc-list-heading" in item.get_attribute("class"):
                                                date = item.get_attribute("data-date")
                                                file.write(f"  Date: {date}\n")
                                                
                                        break  # Break the retry loop if successful

                                    except StaleElementReferenceException:
                                        retry_count -= 1
                                        print("Stale element reference, retrying...")

                                    except ElementClickInterceptedException:
                                        print("Element click intercepted, trying to close the panel and retry...")
                                        close_panel_if_open(driver)
                                        retry_count -= 1

                                file.write("\n" + "="*40 + "\n\n")
            break

finally:
    driver.quit()
