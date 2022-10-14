import os
import util

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


def log_in_to_messenger() -> bool:
    """
    Method that logs in to messenger
    :return: True if logging in was successful
    """
    # 0. Check env
    #       0.1. Check that fernet_key exists
    fernet_key = util.get_fernet_key()

    #       0.2. Read credentials.json
    credentials_dict = util.read_credentials()

    # 1. Open messenger.com
    driver = webdriver.Firefox()
    driver.get('https://messenger.com')

    #       1.1. Accept basic cookies
    _press_element(driver, element_to_find="//button[@data-testid='cookie-policy-manage-dialog-accept-button']")

    # 2. Enter login details
    #       2.0. Decode credentials
    credentials_dict = util.decode_credentials(
        credentials=credentials_dict,
        fernet_key=fernet_key
    )

    #       2.1. Enter login
    _enter_input(driver, input_element="//input[@id='email']", input_text=credentials_dict['login'])

    #       2.2. Enter pass
    _enter_input(driver, input_element="//input[@id='pass']", input_text=credentials_dict['password'])

    #       2.3. Press log in
    _press_element(driver, element_to_find="//button[@id='loginbutton']")

    # 3. Go through 2fa process
    #       3.1. Accept 2fa process
    _press_element(driver, element_to_find="//a[@role='button']")

    #       3.2. Confirm cookies on facebook.com now
    _press_element(driver, element_to_find="//button[@data-testid='cookie-policy-manage-dialog-accept-button']")

    #       3.3. Enter 2fa code
    current_2fa_code = util.get_current_2fa_code(credentials_dict['totp_code'])
    _enter_input(driver, input_element="//input[@id='approvals_code']", input_text=current_2fa_code)

    # 4. Make messenger trust the driver
    in_checkpoint = True
    while in_checkpoint:
        in_checkpoint = _press_element(driver, element_to_find="//button[@id='checkpointSubmitButton']")

    return True


def wait_until_found_and_return_element(
        driver: webdriver,
        look_by: By,
        look_for: str,
        time_to_wait: int = 20
):
    element = WebDriverWait(driver, time_to_wait).until(
        expected_conditions.visibility_of_element_located((look_by, look_for))
    )
    return element


def press_enter(driver):
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)
    actions.perform()


def _press_element(driver: webdriver, element_to_find: str) -> bool:
    element_found = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=element_to_find
    )
    if element_found:
        element_found.click()
        return True

    return False


def _enter_input(driver: webdriver, input_element: str, input_text: str) -> bool:
    _input_element = wait_until_found_and_return_element(
        driver=driver,
        look_by=By.XPATH,
        look_for=input_element
    )

    if _input_element:
        _input_element.click()
        _input_element.send_keys(input_text)
        return True

    return False
