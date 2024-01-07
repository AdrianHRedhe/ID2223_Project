import re
import sys
import time
import logging
import requests
import mybrowser
import pandas as pd
from random import uniform
from datetime import datetime 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def rand_sleep(almost_time, diff=0.2):
    ub = almost_time+diff
    lb = almost_time-diff
    actual_sleep_time = uniform(lb,ub)
    time.sleep(actual_sleep_time)
    return

def goto_url(driver):
    url = 'https://www.google.com/maps/'
    driver.get(url)
    return

def accept_google_control_page(driver):
    # If IP in eu then you need to accept cookies
    try:
        driver.find_element(By.CSS_SELECTOR,'[aria-label = "Accept all"]').click()
    except Exception as e:
        driver.save_screenshot('No Google Or is it.png')
        print(f"No google-control page / Issues with language")
    return

def get_next_location(path_to_result_log, path_to_locations):
    result_log = pd.read_csv(path_to_result_log)
    locations = pd.read_csv(path_to_locations)
    
    previous_id = result_log.new_order_id.max()
    new_id = previous_id + 1

    mask = [id == new_id for id in locations.new_order_id]
    location = locations[mask]['Google Location'].iloc[0]

    return location, new_id

def search_google(driver, place):
    # Go to the actual coordinates
    driver.find_element(By.CSS_SELECTOR,'[id="searchboxinput"]').send_keys(f'{place}')
    driver.find_element(By.CSS_SELECTOR,'[id="searchbox-searchbutton"]').click()
    return

def go_to_streetview(driver):
    buttons = driver.find_elements(By.TAG_NAME,'button')
    disp_buttons = [button for button in buttons if button.is_displayed() == True]
    aria_label_empty_buttons = [button for button in disp_buttons if button.get_attribute('aria-label') == '']
    if len(aria_label_empty_buttons) == 1:
        button = aria_label_empty_buttons[0]
        button.click()
        return True, len(buttons)
    return False, len(buttons)

# HMM kanske mer värt att ta mer tid emellan försöken här?
def try_to_go_to_streetview(driver,max_retries,time_to_sleep):
    prev_n_buttons = 0
    
    for _ in range(max_retries):
        rand_sleep(time_to_sleep)
        
        success, cur_n_buttons = go_to_streetview(driver)
        
        print(f'Did go to SV: {success}')
        if success:
            return True

        if cur_n_buttons == prev_n_buttons:
            return False

        prev_n_buttons = cur_n_buttons

    return False

def screenshot(driver, output_dir, id, imgNumber, button_id, taken_when=''):
    fname = f'{output_dir}/{id}_{imgNumber}_{button_id}'
    if not taken_when == '':
        fname += f'_{taken_when}'
    fname += f'_{str(datetime.now())}.png'

    with open(fname, 'xb') as f:
        canvas = driver.find_element(By.TAG_NAME,'canvas')
        
        '''
        try:
            ActionChains(driver)\
                .move_by_offset(100,100)\
                .perform()
            time.sleep(0.9)
        finally:
        '''
        f.write(canvas.screenshot_as_png)
    return
        
def rotate45deg(driver):
    main = driver.find_element(By.CLASS_NAME,'widget-scene')
    action = ActionChains(driver)
    action.drag_and_drop_by_offset(main,450,0).perform()
    return

def rotate90deg(driver):
    main = driver.find_element(By.CLASS_NAME,'widget-scene')
    sub = driver.find_element(By.ID,'omnibox-container')
    action = ActionChains(driver)
    
    # make sure it is engaged
    action.drag_and_drop_by_offset(main,10,0).drag_and_drop_by_offset(main,-10,0).perform()
    rand_sleep(0.3)
    # Turn 90 degrees
    action.key_down('d').perform()
    time.sleep(1.125)
    action.key_up('d').perform()

    # Hide the mouse
    action.move_to_element(sub).perform()
    return

def rotate90deg_improved(driver):
    buttons = driver.find_elements(By.TAG_NAME,'button')
    disp_buttons = [button for button in buttons if button.is_displayed() == True]
    rotateButtons = [button for button in disp_buttons if button.get_attribute('aria-label') == 'Rotate the view counterclockwise']
    if not len(rotateButtons) == 1:
        return False

    rotateButtons[0].click()
    return True

def open_timemachine(driver):
    buttons = driver.find_elements(By.TAG_NAME,'button')
    disp_buttons = [button for button in buttons if button.is_displayed() == True]
    timemachineButtons = [button for button in disp_buttons if button.get_attribute('jsaction') == 'titlecard.timemachineClick']
    
    if not len(timemachineButtons) == 1:
        return False
    
    timemachineButtons[0].click()
    return True

def format_correct(button):
    pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})"
    label = button.get_attribute('aria-label')
    label_str = str(label)
    is_a_match = re.match(pattern, label_str)
    return is_a_match

def find_timemachine_buttons(driver):
    buttons = driver.find_elements(By.TAG_NAME,'button')
    disp_buttons = [button for button in buttons if button.is_displayed() == True]
    print(f'TM Buttons Disp: {len(disp_buttons)}')
    correctly_formated_buttons = [button for button in disp_buttons if format_correct(button)]
    if len(correctly_formated_buttons) == 0:
        tmp_display = [button.get_attribute('aria-label') for button in disp_buttons]
        print(tmp_display)
        print('Error: Cant find the TM buttons')
    return correctly_formated_buttons

def current_timemachine_button(tm_buttons):
    for b in tm_buttons:
        jslog = b.get_attribute('jslog')
        if 'metadata' in jslog:
            return b
    return None

def circle_through_all_tms(driver, output_dir, id):
    success = try_to_go_to_streetview(driver,max_retries=3,time_to_sleep=10)

    if not success:
        raise Exception('Error: Could not go to GSV')

    print('OK - Is ready for TM')

    rand_sleep(5)
    if not open_timemachine(driver):
        rand_sleep(5)
        if not open_timemachine(driver):
            raise Exception('Error: Could not open TM')
    
    print('TM - OK')
   
    try:
        time.sleep(0.2)
        rotate90deg_improved(driver)

    except Exception as e:
        raise Exception(f'Error: with first rotation | {e}')
    
    
    try:
        tm_buttons = find_timemachine_buttons(driver)
        if len(tm_buttons) == 0:
            print('Trying to find tm_buttons again')
            rand_sleep(5)
            tm_buttons = find_timemachine_buttons(driver)
            if len(tm_buttons) == 0:
                raise Exception(f'Error: There seems to be no tm_buttons')
    except Exception as e:
        raise Exception(f'Error: with finding TM buttons | {e}')

    try:
        taken_whens  = [button.get_attribute('aria-label') for button in tm_buttons]
        number_of_screenshots = 4

        for imgNumber in range(number_of_screenshots):
            rand_sleep(1)

            for button_id, button in enumerate(tm_buttons):
                taken_when = taken_whens[button_id]
                rand_sleep(1)
                button.click()
                rand_sleep(5)
                screenshot(driver, output_dir, id, imgNumber, button_id, taken_when)

            rand_sleep(1)
            rotate90deg_improved(driver)
            rand_sleep(0.5)

    except Exception as e:
        raise Exception(f'Error: Issues when taking the images | {e}')

    return True

def general_start(path_to_result_log, path_to_locations):
    driver = mybrowser.MyBrowserClass.start_browser()
    driver.set_window_size(1512,895)

    try:
        goto_url(driver)
    except:
        raise Exception('Could not open URL')
        
    try:
        rand_sleep(0.5)
        accept_google_control_page(driver)
    except:
        raise Exception('Ran into issue on control page')

    try:
        place, id = get_next_location(path_to_result_log, path_to_locations)
    except Exception as e:
        raise Exception(f'Could not get the location | {e}')

    try:
        rand_sleep(5)
        search_google(driver, place)
    except:
        try:
            rand_sleep(5)
            search_google(driver, place)
        except:
            raise Exception('Could not Search, Could be issue with google control page')
    return driver, id

def start_logging():
    logging.basicConfig(
        filename="log.txt",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

def logError(msg):
    logging.error(f'An error occurred: {msg}', exc_info=True)
    return

def save_results(path, id, status):
    result_log = pd.read_csv(path)
    result_log_new_entry = {'new_order_id': id,'status': status}
    result_log_new_entry_df = pd.DataFrame(result_log_new_entry,index=[0])
    result_log_updated = pd.concat([result_log, result_log_new_entry_df], axis=0)
    result_log_updated.to_csv(path,index=False)

def full_run():
    try:
        start_time = datetime.now()
        output_dir = './Volume'
        path_to_result_log = 'result_log.csv'
        path_to_locations = 'new_order_buffer_100.csv'

        start_logging()

        try:
            mybrowser.MyBrowserClass.set_new_ip()
            response = requests.get('http://icanhazip.com/', proxies={'http': '127.0.0.1:8118'})
            print(f'IP: {response.text.strip()} Started at: {datetime.now()}')
        except Exception as e:
            logError(e)
            raise Exception(e)
            
        try:
            driver, id = general_start(path_to_result_log, path_to_locations)
        except Exception as e:
            logError(e)
            raise Exception(f'Could not start run | {e}')

        try:
            circle_through_all_tms(driver, output_dir, id)
        except Exception as e:
            msg = f'Run failed for id {id} | {e}'
            logError(msg)
            save_results(path_to_result_log, id, status='Failure')
        
            raise Exception(msg)
    
        logging.info(f'Run finished successfully for id: {id}')
        save_results(path_to_result_log, id, status='Success')
        print(f'Run finished successfully for id: {id}')

    except Exception as e:
        print(e)

    finally:
        driver.quit()
        print(datetime.now()-start_time)

for i in range(100):
    print(f'run {i}')
    try:
        full_run()
    except UnboundLocalError as e:
        print(e)
    finally:
        print('\n')


# mybrowser.MyBrowserClass.set_new_ip()
# time.sleep(6)
# driver= mybrowser.restart_browser(mybrowser.MyBrowserClass, driver)
