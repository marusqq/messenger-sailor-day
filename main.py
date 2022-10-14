import util
from common_selenium_methods import (
    log_in_to_messenger,
    enter_input,
    press_element,
    find_and_get_element,
    wait_for_element_to_load,
    find_and_get_elements, clear_element
)

logged_in, driver = log_in_to_messenger(headless=True, maximise=True)

video_group_url = "8455050194520025"


group_ids = {
    "100000105556453": ""
}

if logged_in:

    group_ids_with_names = {}

    # 1. get names from group ids
    for group_id, group_name in group_ids.items():
        driver.get(f"https://www.messenger.com/t/{group_id}")
        # if the group didn't load in 20 secs, go to next group id
        if not wait_for_element_to_load(driver, element_to_find="//a[starts-with(@aria-label, 'Chats')]"):
            continue

        # try to find a single person (PM) name
        href_xpath = f"https://www.facebook.com/{group_id}/"
        group_name_element = find_and_get_element(driver, element_to_find=f"//a[@href='{href_xpath}']")
        if group_name_element:
            if group_name_element.get_attribute('aria-label'):
                group_ids_with_names[group_id] = group_name_element.get_attribute('aria-label')

        # if not found - try looking for a group name
        if group_name_element is None:
            group_name_element = find_and_get_element(
                driver, element_to_find="//div[starts-with(@aria-label, 'Conversation titled')]")
            if group_name_element:
                group_ids_with_names[group_id] = \
                    group_name_element.get_attribute('aria-label').split("Conversation titled ")[1]

    # 2. determine what day it is
    weekday = util.get_weekday()

    # 3. find the correct day video
    driver.get(f"https://www.messenger.com/t/{video_group_url}")
    # if the group didn't load in 20 secs, go to next group id
    if not wait_for_element_to_load(driver, element_to_find="//a[starts-with(@aria-label, 'Chats')]"):
        raise SystemExit(f"Group that has videos failed to load. Group_id: {video_group_url}")

    # find all the possible forwards
    video_forward_elements = find_and_get_elements(
        driver, element_to_find="//div[@aria-label='Forward']")

    # scroll_to_top_once(driver)
    # weekday = 5 - 1 = 4

    # maybe
    # 0 sunday
    # 1 saturday
    # 2 friday
    # 3 thursday
    # 4 wednesday
    # 5 tuesday
    # 6 monday

    video_forward_elements[7 - weekday].click()

    util.make_screenshot(driver)

    # 4. forward it to all group ids that have a name and only if that name only gives one send button

    # for every group to send
    for _, group_name in group_ids_with_names.items():
        press_element(driver, element_to_find="//input[@aria-label='Search for people and groups']", time_to_wait=30)

        clear_element(driver, element_to_find="//input[@aria-label='Search for people and groups']")

        enter_input(driver, input_element="//input[@aria-label='Search for people and groups']", input_text=group_name)

        press_element(driver, element_to_find="//div[@aria-label='Send']")

        wait_for_element_to_load(driver, element_to_find="//div[@aria-label='Sent']", time_to_wait=40)

    driver.quit()
