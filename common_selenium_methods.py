import time
from typing import Tuple, Optional, List

from selenium.common import TimeoutException
from selenium.webdriver.firefox.webdriver import WebDriver

import util

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebElement


def log_in_to_messenger(headless: bool = False, maximise: bool = False) -> Tuple[bool, WebDriver]:
    """
    Method that logs in to messenger
    :return: True if logging in was successful
    """
    # 0. Check env
    #       0.1. Check that fernet_key exists
    fernet_key = util.get_fernet_key()

    #       0.2. Read credentials.json
    credentials_dict = util.read_credentials()

    #       0.3. Setup FirefoxOptions
    options = FirefoxOptions()
    if headless:
        options.add_argument("--headless")

    # 1. Open messenger.com
    driver = webdriver.Firefox(options=options)
    driver.get('https://messenger.com')

    if maximise:
        driver.fullscreen_window()

    #       1.1. Accept basic cookies
    press_element(
        driver, time_to_wait=10,
        element_to_find="//button[@data-testid='cookie-policy-manage-dialog-accept-button']"
    )

    # 2. Enter login details
    #       2.0. Decode credentials
    credentials_dict = util.decode_credentials(
        credentials=credentials_dict,
        fernet_key=fernet_key
    )

    #       2.1. Enter login
    enter_input(driver, input_element="//input[@id='email']", input_text=credentials_dict['login'])

    #       2.2. Enter pass
    enter_input(driver, input_element="//input[@id='pass']", input_text=credentials_dict['password'])

    #       2.3. Press log in
    press_element(driver, element_to_find="//button[@id='loginbutton']")

    # 3. Go through 2fa process
    #       3.1. Accept 2fa process
    press_element(driver, element_to_find="//a[@role='button']")

    #       3.2. Confirm cookies on facebook.com now
    press_element(
        driver, time_to_wait=10,
        element_to_find="//button[@data-testid='cookie-policy-manage-dialog-accept-button']"
    )

    #       3.3. Enter 2fa code
    current_2fa_code = util.get_current_2fa_code(credentials_dict['totp_code'])
    enter_input(driver, input_element="//input[@id='approvals_code']", input_text=current_2fa_code)

    # 4. Make messenger trust the driver
    in_checkpoint = True
    while in_checkpoint:
        in_checkpoint = press_element(driver, element_to_find="//button[@id='checkpointSubmitButton']")
        time.sleep(2)

    if not wait_for_element_to_load(driver, element_to_find="//a[starts-with(@aria-label, 'Chats')]"):
        util.make_screenshot(driver)
        return False, driver

    # 5. Check if driver's url changed to something like: https://www.messenger.com/t/xxxxxxxxxxxxxxxxxx/
    if 'messenger.com/t/' in driver.current_url:
        return True, driver

    util.make_screenshot(driver)
    return False, driver


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


def press_enter(driver):
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)
    actions.perform()


def press_element(driver: webdriver, element_to_find: str, time_to_wait=20) -> bool:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_to_find,
        time_to_wait=time_to_wait
    )
    if element_found is not None:
        element_found.click()
        return True
    return False


def find_and_get_element(driver: webdriver, element_to_find: str, time_to_wait=20) -> Optional[WebElement]:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_to_find,
        time_to_wait=time_to_wait
    )
    if element_found is not None:
        return element_found
    return None


def find_and_get_elements(driver: webdriver, element_to_find: str, time_to_wait=30) -> List[WebElement]:
    elements_found = wait_until_found_and_return_elements(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_to_find,
        time_to_wait=time_to_wait
    )
    if len(elements_found):
        return elements_found
    return []


def wait_for_element_to_load(driver: webdriver, element_to_find: str, time_to_wait=20) -> bool:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_to_find,
        time_to_wait=time_to_wait
    )
    if element_found is not None:
        return True
    return False


def enter_input(driver: webdriver, input_element: str, input_text: str) -> bool:
    _input_element = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=input_element
    )

    if _input_element is not None:
        _input_element.click()
        ActionChains(driver).send_keys_to_element(_input_element, input_text).perform()
        return True
    return False


def clear_element(driver: webdriver, element_to_find: str, time_to_wait=20) -> bool:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_to_find,
        time_to_wait=time_to_wait
    )
    if element_found:
        element_found.clear()
        return True
    return False


def scroll_to_top_once(driver):
    scroll_pause_time = 3

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
