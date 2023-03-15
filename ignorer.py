import time
from typing import List, Optional
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, MoveTargetOutOfBoundsException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from common_selenium_methods import log_in_to_messenger

GROUP_ID = 6099761460094553

IGNORE_LIST = {
    "Titas Kvederys": ""
}


def wait_until_found_and_return_element(
        driver: webdriver,
        look_by: By,
        look_for: str,
        time_to_wait: int = 20
) -> Optional[WebElement]:
    try:
        element = WebDriverWait(driver, time_to_wait).until(
            expected_conditions.visibility_of_element_located((look_by, look_for))
        )
        return element

    except TimeoutException:
        return None


def wait_for_element_to_load(driver: webdriver, element_xpath: str, time_to_wait=20) -> bool:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_xpath,
        time_to_wait=time_to_wait
    )
    if element_found is not None:
        return True

    return False


def wait_until_found_and_return_elements(
        driver: webdriver,
        look_by: By,
        look_for: str,
        time_to_wait: int = 20
) -> List[WebElement]:
    try:
        elements = WebDriverWait(driver, time_to_wait).until(
            expected_conditions.presence_of_all_elements_located((look_by, look_for))
        )
        return elements

    except TimeoutException:
        return []


def get_nickname_by_name(ignore_list):
    # open settings of conversation
    # conversation_settings_button = wait_until_found_and_return_elements(
    #     driver,
    #     look_by=By.XPATH,
    #     look_for="//a[starts-with(@aria-label, 'Conversation information')]",
    #     time_to_wait=20,
    # )[0]
    # conversation_settings_button.click()

    return {"Titas Kvederys": "90"}


def scroll_to_element(driver, element):
    actions = ActionChains(driver)
    try:
        actions.move_to_element(element).perform()
    except MoveTargetOutOfBoundsException as e:
        print(e)
        driver.execute_script("arguments[0].scrollIntoView(true);", element)


driver = log_in_to_messenger(headless=False, maximise=False, disable_gpu=True)

# load that group
driver.get(f"https://www.messenger.com/t/{GROUP_ID}")
if not wait_for_element_to_load(driver, element_xpath="//a[starts-with(@aria-label, 'Chats')]"):
    driver.quit()
    raise SystemExit(f"Failed loading group_id: {GROUP_ID}")

IGNORE_LIST = get_nickname_by_name(ignore_list=IGNORE_LIST)

# reload that group
driver.get(f"https://www.messenger.com/t/{GROUP_ID}")

# start to look for messages
while True:
    time.sleep(3)

    messages = driver.find_elements(
        by=By.XPATH,
        value="//div[starts-with(@aria-label, 'Messages in conversation titled')]/div"
    )
    print(f"Messages found: {len(messages)}")

    for message in messages:

        print('click on msg')
        message_sender_nickname = message.find_element(by=By.XPATH, value='.//div/div/span').text
        print(f"Messenger sender nickname: {message_sender_nickname}")

        # if sender is in ignore list - delete
        if message_sender_nickname in IGNORE_LIST.values():
            print(f"HES IGNORED: {IGNORE_LIST.values()}")

            scroll_to_element(driver, message)

            time.sleep(2)

            delete_menu = wait_until_found_and_return_elements(
                driver,
                look_by=By.XPATH,
                look_for="//div[starts-with(@aria-label, 'Menu')]",
                time_to_wait=10
            )[0]
            print('find delete menu')
            delete_menu.click()
            print(f"click open delete menu")

            remove_message_btn = wait_until_found_and_return_elements(
                driver,
                look_by=By.XPATH,
                look_for="//div[starts-with(@aria-label, 'Remove message')]",
                time_to_wait=5
            )[0]
            remove_message_btn.click()
            print(f"REMOVING MESSAGE")

            remove_message_confirm_btn = wait_until_found_and_return_elements(
                driver,
                look_by=By.XPATH,
                look_for="//div[starts-with(@aria-label, 'Remove')]",
                time_to_wait=5
            )[0]
            remove_message_confirm_btn.click()
            print(f"CONFIRMING")
